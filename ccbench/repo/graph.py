"""Static program graph over code units.

Two graphs are built from the same index:

* ``ProgramGraph``  - import-aware name resolution, class hierarchy analysis
  (CHA: self-calls also reach overriding methods in subclasses), super() calls,
  instantiation, constant references, and *dispatch* edges that follow common
  Python plug-in conventions:
    - registry:  ``resolve(kind, X)``  -> classes decorated ``@register(kind, ..)``;
                 when X comes from a settings key, configured names rank higher
    - config:    ``settings.get("key")`` -> config dict literals defining "key"
    - events:    ``publish("topic", ..)`` -> functions decorated ``@subscribe("topic")``
    - routes:    ``dispatch(method, path)`` -> functions decorated ``@route(..)``
  Dispatch edges can be switched off (ablation ``-dispatch``).

* ``NameGraph``     - naive baseline: a call to ``foo`` links to *every* unit
  named ``foo`` anywhere in the repository (what a grep-based tool would do).

The conventions are matched by decorator/function *names* and literal
arguments, not by fixture-specific identifiers. That is still an assumption
about the code base and is reported as a threat to validity.
"""

import ast
from collections import defaultdict

DISPATCH_KINDS = {"registry", "config", "event", "route"}

W = {
    "call": 1.0, "self_call": 0.9, "override": 0.8, "super_call": 0.9, "instantiate": 0.9,
    "ref": 0.7, "member_of": 0.9, "has_member": 0.45, "inherits": 0.85, "subclass": 0.6,
    "import_module": 0.35, "registry": 0.95, "registry_other": 0.3, "registry_profile": 0.6,
    "config": 0.7, "event": 0.95, "route": 0.3, "typed_call": 0.9, "duck_call": 0.5, "duck_call_weak": 0.3,
}

GENERIC_METHODS = {"get", "items", "append", "extend", "update", "pop", "keys", "values", "join", "split",
                   "replace", "strip", "lower", "upper", "format", "setdefault", "sort", "add", "copy",
                   "quantize", "to_integral_value", "weekday", "isalnum", "count", "select", "insert"}


class Edge:
    __slots__ = ("src", "dst", "kind", "weight", "reverse")

    def __init__(self, src, dst, kind, weight, reverse=False):
        self.src, self.dst, self.kind, self.weight, self.reverse = src, dst, kind, weight, reverse

    @property
    def family(self):
        base = self.kind.split("_")[0]
        return "dispatch" if base in DISPATCH_KINDS else "static"


def _literal_str(node):
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    return None


def _call_name(call):
    f = call.func
    if isinstance(f, ast.Name):
        return f.id
    if isinstance(f, ast.Attribute):
        return f.attr
    return None


class ProgramGraph:
    def __init__(self, index, dispatch=True):
        self.index = index
        self.dispatch = dispatch
        self.out = defaultdict(list)
        self.inn = defaultdict(list)
        self.imports = {}       # path -> {local: ("module", mod) | ("symbol", mod, name)}
        self.defs = {}          # path -> {name: unit_id}
        self.consts = {}        # path -> set(names)
        self.class_bases = {}   # class unit id -> [class unit ids]
        self.class_methods = {} # class unit id -> {method name: unit id}
        self.subclasses = defaultdict(list)
        self.registry = defaultdict(list)    # kind -> [(name, class unit id)]
        self.subscribers = defaultdict(list) # topic -> [unit ids]
        self.routes = {}                     # (method, path) -> unit id
        self.config_values = defaultdict(list)  # key -> [(value, is_default)]
        self.config_units = defaultdict(set)    # key -> unit ids defining it
        self.attr_types = defaultdict(dict)     # class unit id -> {attr: class unit id}
        self.methods_by_name = defaultdict(list)
        self._edge_index = {}
        self._collect()
        self._link()

    # ------------------------------------------------------------- collection
    def _collect(self):
        idx = self.index
        for path, tree in idx.trees.items():
            imp, defs, consts = {}, {}, set()
            mod = idx.module_name(path)
            for node in ast.walk(tree):
                if isinstance(node, ast.ImportFrom) and node.module:
                    base = node.module
                    if node.level:
                        parts = mod.split(".")
                        base = ".".join(parts[: len(parts) - node.level + (1 if path.endswith("__init__.py") else 0)] + [node.module])
                    for a in node.names:
                        imp[a.asname or a.name] = ("symbol", base, a.name)
                elif isinstance(node, ast.Import):
                    for a in node.names:
                        imp[a.asname or a.name.split(".")[0]] = ("module", a.name if a.asname else a.name.split(".")[0])
            for node in tree.body:
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                    defs[node.name] = "%s::%s" % (path, node.name)
                elif isinstance(node, (ast.Assign, ast.AnnAssign)):
                    targets = node.targets if isinstance(node, ast.Assign) else [node.target]
                    for t in targets:
                        if isinstance(t, ast.Name):
                            consts.add(t.id)
                    self._collect_config(path, node)
            self.imports[path], self.defs[path], self.consts[path] = imp, defs, consts
        # class hierarchy + decorators
        for u in idx.units.values():
            if u.kind == "class":
                self.class_methods[u.id] = {
                    m.name: m.id for m in idx.units.values() if m.kind == "method" and m.path == u.path and m.cls == u.name
                }
        for u in idx.units.values():
            if u.kind == "method":
                self.methods_by_name[u.name].append(u.id)
                for n in ast.walk(u.node):
                    if (isinstance(n, ast.Assign) and len(n.targets) == 1 and isinstance(n.targets[0], ast.Attribute)
                            and isinstance(n.targets[0].value, ast.Name) and n.targets[0].value.id == "self"
                            and isinstance(n.value, ast.Call)):
                        for t in self._resolve_expr(u.path, n.value.func):
                            if t in self.class_methods:
                                self.attr_types["%s::%s" % (u.path, u.cls)][n.targets[0].attr] = t
        for u in idx.units.values():
            if u.kind == "class":
                bases = []
                for b in u.node.bases:
                    bases.extend(t for t in self._resolve_expr(u.path, b) if t in self.class_methods)
                self.class_bases[u.id] = bases
                for b in bases:
                    self.subclasses[b].append(u.id)
            if u.kind in ("class", "function", "method"):
                for d in getattr(u.node, "decorator_list", []):
                    if isinstance(d, ast.Call):
                        name = _call_name(d)
                        args = [_literal_str(a) for a in d.args]
                        if name == "register" and len(args) >= 2 and args[0] and args[1]:
                            self.registry[args[0]].append((args[1], u.id))
                        elif name == "subscribe" and args and args[0]:
                            self.subscribers[args[0]].append(u.id)
                        elif name == "route" and len(args) >= 2 and args[0] and args[1]:
                            self.routes[(args[0].upper(), args[1])] = u.id

    def _collect_config(self, path, node):
        value = getattr(node, "value", None)
        dicts = [n for n in ast.walk(value) if isinstance(n, ast.Dict)] if value is not None else []
        target = node.targets[0] if isinstance(node, ast.Assign) else node.target
        is_default = isinstance(target, ast.Name) and target.id.upper() == "DEFAULTS"
        unit_id = "%s::<module>" % path
        for d in dicts:
            for k, v in zip(d.keys, d.values):
                key = _literal_str(k) if k is not None else None
                if not key or "." not in key:
                    continue
                self.config_units[key].add(unit_id)
                vals = []
                if _literal_str(v):
                    vals = [_literal_str(v)]
                elif isinstance(v, (ast.List, ast.Tuple)):
                    vals = [_literal_str(e) for e in v.elts if _literal_str(e)]
                for val in vals:
                    self.config_values[key].append((val, is_default))

    # ------------------------------------------------------------- resolution
    def _resolve_symbol(self, module, name, depth=0):
        idx = self.index
        path = idx.path_for_module(module)
        if path is None:
            sub = idx.path_for_module(module + "." + name)
            return [sub + "::<module>"] if sub and (sub + "::<module>") in idx.units else []
        if name in self.defs.get(path, {}):
            return [self.defs[path][name]]
        if name in self.consts.get(path, set()):
            return [path + "::<module>"]
        sub = idx.path_for_module(module + "." + name)
        if sub:
            return [sub + "::<module>"] if (sub + "::<module>") in idx.units else []
        imp = self.imports.get(path, {}).get(name)
        if imp and imp[0] == "symbol" and depth < 3:
            return self._resolve_symbol(imp[1], imp[2], depth + 1)
        return []

    def _resolve_name(self, path, name):
        if name in self.defs.get(path, {}):
            return [self.defs[path][name]]
        if name in self.consts.get(path, set()):
            return [path + "::<module>"]
        imp = self.imports.get(path, {}).get(name)
        if imp and imp[0] == "symbol":
            return self._resolve_symbol(imp[1], imp[2])
        return []

    def _resolve_expr(self, path, node):
        if isinstance(node, ast.Name):
            return self._resolve_name(path, node.id)
        if isinstance(node, ast.Attribute):
            chain = []
            cur = node
            while isinstance(cur, ast.Attribute):
                chain.append(cur.attr)
                cur = cur.value
            if isinstance(cur, ast.Name):
                imp = self.imports.get(path, {}).get(cur.id)
                if imp and imp[0] == "module":
                    dotted = ".".join([imp[1]] + list(reversed(chain)))
                    mod, _, name = dotted.rpartition(".")
                    return self._resolve_symbol(mod, name)
        return []

    def lookup_method(self, cls_id, name, seen=None):
        seen = seen or set()
        if cls_id in seen:
            return []
        seen.add(cls_id)
        if name in self.class_methods.get(cls_id, {}):
            return [self.class_methods[cls_id][name]]
        for b in self.class_bases.get(cls_id, []):
            found = self.lookup_method(b, name, seen)
            if found:
                return found
        return []

    def overrides(self, cls_id, name):
        out, stack = [], list(self.subclasses.get(cls_id, []))
        while stack:
            c = stack.pop()
            if name in self.class_methods.get(c, {}):
                out.append(self.class_methods[c][name])
            stack.extend(self.subclasses.get(c, []))
        return out

    # ------------------------------------------------------------- linking
    def add(self, src, dst, kind):
        if src == dst or dst not in self.index.units:
            return
        if not self.dispatch and kind.split("_")[0] in DISPATCH_KINDS:
            return
        w = W[kind]
        key = (src, dst)
        old = self._edge_index.get(key)
        if old is not None:
            if old.weight >= w:
                return
            self.out[src].remove(old)
            self.inn[dst] = [e for e in self.inn[dst] if e.dst != src]
        e = Edge(src, dst, kind, w)
        self._edge_index[key] = e
        self.out[src].append(e)
        self.inn[dst].append(Edge(dst, src, kind, w, reverse=True))

    def _link(self):
        idx = self.index
        for u in idx.units.values():
            cls_id = "%s::%s" % (u.path, u.cls) if u.kind == "method" else None
            if u.kind == "method":
                self.add(u.id, cls_id, "member_of")
                self.add(cls_id, u.id, "has_member")
            if u.kind == "class":
                for b in self.class_bases.get(u.id, []):
                    self.add(u.id, b, "inherits")
                    self.add(b, u.id, "subclass")
            if u.kind == "module":
                for local, imp in self.imports[u.path].items():
                    if imp[0] == "module" or (imp[0] == "symbol" and self.index.path_for_module(imp[1] + "." + imp[2])):
                        target_mod = imp[1] if imp[0] == "module" else imp[1] + "." + imp[2]
                        p = idx.path_for_module(target_mod)
                        if p:
                            self.add(u.id, p + "::<module>", "import_module")
            self._link_body(u, cls_id)

    def _scope_nodes(self, u):
        if u.kind == "module":
            for stmt in u.node.body:
                if not isinstance(stmt, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                    yield from ast.walk(stmt)
        elif u.kind == "class":
            for d in u.node.decorator_list:
                yield from ast.walk(d)
            for stmt in u.node.body:
                if not isinstance(stmt, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    yield from ast.walk(stmt)
        else:
            yield from ast.walk(u.node)

    def _settings_keys_in(self, u):
        keys = []
        for n in ast.walk(u.node) if u.node is not None else []:
            if isinstance(n, ast.Call) and _call_name(n) in ("get", "require") and n.args:
                k = _literal_str(n.args[0])
                if k and k in self.config_values:
                    keys.append(k)
        return keys

    def _link_body(self, u, cls_id):
        keys = None
        for n in self._scope_nodes(u):
            if isinstance(n, ast.Call):
                self._link_call(u, cls_id, n)
                name = _call_name(n)
                args = [_literal_str(a) for a in n.args]
                if name in ("get", "require") and args and args[0] in self.config_units:
                    for cu in self.config_units[args[0]]:
                        self.add(u.id, cu, "config")
                elif name == "resolve" and args and args[0] in self.registry:
                    if keys is None:
                        keys = self._settings_keys_in(u)
                    literal = args[1] if len(args) > 1 else None
                    default_vals = {v for k in keys for v, d in self.config_values[k] if d}
                    profile_vals = {v for k in keys for v, d in self.config_values[k] if not d}
                    for reg_name, target in self.registry[args[0]]:
                        if literal is not None:
                            kind = "registry" if reg_name == literal else None
                        elif reg_name in default_vals:
                            kind = "registry"
                        elif reg_name in profile_vals:
                            kind = "registry_profile"
                        else:
                            kind = "registry_other"
                        if kind:
                            self.add(u.id, target, kind)
                elif name == "publish" and args and args[0]:
                    for s in self.subscribers.get(args[0], []):
                        self.add(u.id, s, "event")
                elif name == "dispatch":
                    for h in self.routes.values():
                        self.add(u.id, h, "route")
            elif isinstance(n, ast.Name) and isinstance(n.ctx, ast.Load):
                for t in self._resolve_name(u.path, n.id):
                    if t != u.id:
                        self.add(u.id, t, "ref")

    def _link_call(self, u, cls_id, call):
        f = call.func
        targets = []
        if isinstance(f, ast.Attribute) and isinstance(f.value, ast.Name) and f.value.id in ("self", "cls") and cls_id:
            for t in self.lookup_method(cls_id, f.attr):
                self.add(u.id, t, "self_call")
            for t in self.overrides(cls_id, f.attr):
                self.add(u.id, t, "override")
            return
        if (isinstance(f, ast.Attribute) and isinstance(f.value, ast.Call)
                and isinstance(f.value.func, ast.Name) and f.value.func.id == "super" and cls_id):
            for b in self.class_bases.get(cls_id, []):
                for t in self.lookup_method(b, f.attr):
                    self.add(u.id, t, "super_call")
            return
        if isinstance(f, ast.Attribute) and not self._resolve_expr(u.path, f):
            recv = f.value
            typed = None
            if (isinstance(recv, ast.Attribute) and isinstance(recv.value, ast.Name)
                    and recv.value.id == "self" and cls_id):
                typed = self._attr_type(cls_id, recv.attr)
            elif isinstance(recv, ast.Name):
                typed = self._local_type(u, recv.id)
            if typed:
                for t in self.lookup_method(typed, f.attr) + self.overrides(typed, f.attr):
                    self.add(u.id, t, "typed_call")
                return
            if f.attr not in GENERIC_METHODS and not f.attr.startswith("__"):
                cands = self.methods_by_name.get(f.attr, [])
                kind = "duck_call" if len(cands) <= 3 else "duck_call_weak"
                for t in cands:
                    self.add(u.id, t, kind)
            return
        targets = self._resolve_expr(u.path, f)
        for t in targets:
            tu = self.index.units.get(t)
            if tu is None:
                continue
            if tu.kind == "class":
                self.add(u.id, t, "instantiate")
                for m in self.lookup_method(t, "__init__"):
                    self.add(u.id, m, "instantiate")
            else:
                self.add(u.id, t, "call")

    def _attr_type(self, cls_id, attr, seen=None):
        seen = seen or set()
        if cls_id in seen:
            return None
        seen.add(cls_id)
        if attr in self.attr_types.get(cls_id, {}):
            return self.attr_types[cls_id][attr]
        for b in self.class_bases.get(cls_id, []):
            t = self._attr_type(b, attr, seen)
            if t:
                return t
        return None

    def _local_type(self, u, name):
        for n in ast.walk(u.node) if u.node is not None else []:
            if (isinstance(n, ast.Assign) and len(n.targets) == 1 and isinstance(n.targets[0], ast.Name)
                    and n.targets[0].id == name and isinstance(n.value, ast.Call)):
                for t in self._resolve_expr(u.path, n.value.func):
                    if t in self.class_methods:
                        return t
        return None

    # ------------------------------------------------------------- queries
    def neighbours(self, uid, reverse=True):
        edges = list(self.out.get(uid, []))
        if reverse:
            edges += self.inn.get(uid, [])
        return edges


class NameGraph:
    """Naive name-matching call graph (baseline E4b)."""

    def __init__(self, index):
        self.index = index
        by_name = defaultdict(list)
        for u in index.units.values():
            if u.kind != "module":
                by_name[u.name].append(u.id)
        self.out = defaultdict(list)
        for u in index.units.values():
            if u.node is None or u.kind == "module":
                continue
            seen = set()
            for n in ast.walk(u.node):
                if isinstance(n, ast.Call):
                    name = _call_name(n)
                    for t in by_name.get(name, []):
                        if t != u.id and t not in seen:
                            seen.add(t)
                            self.out[u.id].append(t)

    def callees(self, uid):
        return self.out.get(uid, [])
