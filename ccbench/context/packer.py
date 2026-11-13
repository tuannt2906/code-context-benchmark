"""Budget-aware packing and rendering of code units into a prompt context."""

import hashlib

from ccbench import tokens


class ContextResult:
    def __init__(self, strategy, budget):
        self.strategy = strategy
        self.budget = budget
        self.full = []        # unit ids included with full body
        self.skeleton = []    # unit ids included as signature only
        self.retrieved = []   # ranked candidate unit ids before packing
        self.text = ""

    @property
    def est_tokens(self):
        return tokens.estimate(self.text)

    def sha(self):
        return hashlib.sha256(self.text.encode()).hexdigest()[:16]

    def meta(self):
        return {
            "strategy": self.strategy,
            "budget": self.budget,
            "context_est_tokens": self.est_tokens,
            "n_full": len(self.full),
            "n_skeleton": len(self.skeleton),
            "n_retrieved": len(self.retrieved),
            "full_units": list(self.full),
            "skeleton_units": list(self.skeleton),
            "context_sha": self.sha(),
        }


def render(index, full_ids, skeleton_ids, file_order=None):
    """Group units by file, each file in line order, files in ``file_order``."""
    chosen = {}
    for uid in full_ids:
        chosen[uid] = "full"
    for uid in skeleton_ids:
        chosen.setdefault(uid, "skeleton")
    by_file = {}
    for uid in chosen:
        u = index.units[uid]
        by_file.setdefault(u.path, []).append(u)
    paths = list(file_order or [])
    paths = [p for p in paths if p in by_file] + sorted(p for p in by_file if p not in paths)
    blocks = []
    for p in paths:
        units = sorted(by_file[p], key=lambda u: u.start)
        body = "\n".join(u.render() if chosen[u.id] == "full" else u.skeleton() for u in units)
        blocks.append("### file: %s\n%s" % (p, body))
    return "\n\n".join(blocks)


def _header_cost(path):
    return tokens.estimate("### file: %s\n\n" % path)


def pack(index, ranked, budget, result, allow_skeleton=False, with_class_header=True):
    """Greedy packing of ranked unit ids into ``budget`` estimated tokens.

    A method pulls in its class header (when ``with_class_header``) so the model
    sees which class it belongs to. Units that do not fit are skipped (or added
    as skeletons when allowed); packing continues with smaller units.
    """
    used, files = 0, set()
    full, skel = [], []
    order = []
    for uid in ranked:
        if uid in full:
            continue
        u = index.units[uid]
        need = [uid]
        if with_class_header and u.kind == "method":
            cid = "%s::%s" % (u.path, u.cls)
            if cid in index.units and cid not in full:
                need.insert(0, cid)
        cost = sum(index.units[x].tokens() + 1 for x in need)
        cost += 0 if u.path in files else _header_cost(u.path)
        if budget is None or used + cost <= budget:
            for x in need:
                if x in skel:
                    skel.remove(x)
                full.append(x)
            used += cost
            files.add(u.path)
            if u.path not in order:
                order.append(u.path)
            continue
        if allow_skeleton and uid not in skel:
            scost = tokens.estimate(u.skeleton()) + 1 + (0 if u.path in files else _header_cost(u.path))
            if budget is None or used + scost <= budget:
                skel.append(uid)
                used += scost
                files.add(u.path)
                if u.path not in order:
                    order.append(u.path)
    result.full, result.skeleton = full, skel
    result.text = render(index, full, skel, order)
    # safety: the estimate of the rendered text must respect the budget
    while budget is not None and result.est_tokens > budget and (result.skeleton or result.full):
        if result.skeleton:
            result.skeleton.pop()
        else:
            result.full.pop()
        result.text = render(index, result.full, result.skeleton, order)
    return result
