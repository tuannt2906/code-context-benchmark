"""Split the fixture repository into addressable code units with AST.

Unit kinds:
  module   top-level statements that are not defs (imports, constants, wiring)
  function top-level function
  class    class header: decorators, class line, docstring, class attributes
  method   method inside a class
Unit ids look like ``frostline/pricing/money.py::round_money`` or
``frostline/pricing/strategies.py::TieredStrategy.base_rate``; module units use
``<module>`` as name.
"""

import ast
import hashlib
import os

from ccbench import tokens


class Unit:
    __slots__ = ("id", "path", "kind", "name", "qualname", "lines", "node", "cls", "src_lines", "_tok")

    def __init__(self, path, kind, qualname, lines, node, src_lines, cls=None):
        self.path = path
        self.kind = kind
        self.qualname = qualname
        self.name = qualname.split(".")[-1]
        self.id = "%s::%s" % (path, qualname)
        self.lines = sorted(set(lines))
        self.node = node
        self.cls = cls
        self.src_lines = src_lines
        self._tok = None

    @property
    def start(self):
        return self.lines[0]

    @property
    def end(self):
        return self.lines[-1]

    def render(self):
        return "\n".join("%4d| %s" % (n, self.src_lines[n - 1]) for n in self.lines)

    def skeleton(self):
        """Signature + first docstring line, for budget-constrained packing."""
        node = self.node
        if self.kind == "module" or node is None:
            return self.render()
        head_end = node.body[0].lineno - 1 if node.body else node.lineno
        first = min([d.lineno for d in getattr(node, "decorator_list", [])] + [node.lineno])
        keep = list(range(first, max(head_end, node.lineno) + 1))
        doc = ast.get_docstring(node)
        out = ["%4d| %s" % (n, self.src_lines[n - 1]) for n in keep if n <= len(self.src_lines)]
        indent = " " * (node.col_offset + 4)
        if doc:
            out.append("    | %s\"\"\"%s\"\"\"" % (indent, doc.strip().splitlines()[0]))
        out.append("    | %s...  # body omitted (lines %d-%d)" % (indent, self.start, self.end))
        return "\n".join(out)

    def text(self):
        return "\n".join(self.src_lines[n - 1] for n in self.lines)

    def tokens(self):
        if self._tok is None:
            self._tok = tokens.estimate(self.render())
        return self._tok


def _stmt_lines(node):
    return range(node.lineno, node.end_lineno + 1)


def _def_lines(node):
    first = min([d.lineno for d in node.decorator_list] + [node.lineno])
    return range(first, node.end_lineno + 1)


class RepoIndex:
    def __init__(self, root, package):
        self.root = root
        self.package = package
        self.units = {}
        self.files = {}
        self.trees = {}
        self._build()

    def _build(self):
        pkg_dir = os.path.join(self.root, self.package)
        for dirpath, dirnames, filenames in os.walk(pkg_dir):
            dirnames[:] = sorted(d for d in dirnames if not d.startswith((".", "__pycache__")))
            for fn in sorted(filenames):
                if fn.endswith(".py"):
                    full = os.path.join(dirpath, fn)
                    rel = os.path.relpath(full, self.root).replace(os.sep, "/")
                    self._index_file(rel, full)

    def _index_file(self, rel, full):
        with open(full, encoding="utf-8") as fh:
            source = fh.read()
        src_lines = source.splitlines()
        self.files[rel] = src_lines
        tree = ast.parse(source)
        self.trees[rel] = tree
        module_lines = []
        for node in tree.body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                self._add(Unit(rel, "function", node.name, _def_lines(node), node, src_lines))
            elif isinstance(node, ast.ClassDef):
                header = set(_def_lines(node))
                for sub in node.body:
                    if isinstance(sub, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        mlines = set(_def_lines(sub))
                        header -= mlines
                        self._add(Unit(rel, "method", "%s.%s" % (node.name, sub.name), mlines, sub,
                                       src_lines, cls=node.name))
                header = [n for n in header if src_lines[n - 1].strip()]
                self._add(Unit(rel, "class", node.name, header, node, src_lines))
            else:
                module_lines.extend(_stmt_lines(node))
        if module_lines:
            self._add(Unit(rel, "module", "<module>", module_lines, tree, src_lines))

    def _add(self, unit):
        self.units[unit.id] = unit

    # ------------------------------------------------------------------ helpers
    def ordered(self):
        """Units in repository order (path, first line)."""
        return sorted(self.units.values(), key=lambda u: (u.path, u.start))

    def by_path(self, path):
        return [u for u in self.ordered() if u.path == path]

    def module_name(self, path):
        mod = path[:-3].replace("/", ".")
        return mod[:-9] if mod.endswith(".__init__") else mod

    def path_for_module(self, module):
        cand = module.replace(".", "/")
        for p in (cand + ".py", cand + "/__init__.py"):
            if p in self.files:
                return p
        return None

    def unit_at(self, path, line):
        for u in self.units.values():
            if u.path == path and line in u.lines:
                return u
        return None

    def def_unit(self, path, lineno):
        """Unit whose def/class statement starts at ``lineno`` (for tracing)."""
        for u in self.units.values():
            if u.path == path and u.node is not None and u.kind != "module" and u.node.lineno == lineno:
                return u
        return None

    def content_hash(self):
        h = hashlib.sha256()
        for path in sorted(self.files):
            h.update(path.encode())
            h.update("\n".join(self.files[path]).encode())
        return h.hexdigest()[:16]

    def total_tokens(self):
        return sum(u.tokens() for u in self.units.values())
