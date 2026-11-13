"""Context construction strategies (experimental conditions E0-E5 + ablations).

Every strategy maps (question, budget) -> ContextResult. Strategies never see
the ground truth, except ``oracle`` (E0), which is the deliberate upper bound.
"""

import heapq
import re

from ccbench.context.bm25 import BM25
from ccbench.context.packer import ContextResult, pack, render
from ccbench.repo.graph import NameGraph, ProgramGraph

FIXED_FILES = [  # E3: the same "architecture overview" files for every question
    "frostline/api/app.py",
    "frostline/config/settings.py",
    "frostline/core/container.py",
    "frostline/api/handlers.py",
    "frostline/pricing/quote_engine.py",
    "frostline/services/shipment_service.py",
    "frostline/services/quote_service.py",
    "frostline/core/registry.py",
    "frostline/core/events.py",
    "frostline/pricing/strategies.py",
]

IMPACT_PAT = re.compile(r"\b(affect|affected|impact|impacted|change[sd]?|differen|would .* differ|callers?|depend)", re.I)
IDENT_PAT = re.compile(r"`([^`]+)`|\b([A-Za-z_][A-Za-z0-9_]*(?:\.[A-Za-z_][A-Za-z0-9_]*)*)\b")
PATH_PAT = re.compile(r"\b((?:frostline/)?[\w/]+\.py)\b")
ROUTE_PAT = re.compile(r"\b(GET|POST|PUT|DELETE)\s+(/[\w/\-]*)")

STRATEGIES = [
    "oracle", "oracle_trace", "none", "full", "fixed", "bm25", "bm25_namegraph", "dgc",
    "dgc_no_dispatch", "dgc_no_expansion", "dgc_no_ranking", "dgc_no_skeleton", "dgc_no_reverse",
]
BUDGET_FREE = {"oracle", "oracle_trace", "none"}

DECAY = 0.8
MIN_SCORE = 0.02


class ContextBuilder:
    def __init__(self, index):
        self.index = index
        self.graph = ProgramGraph(index, dispatch=True)
        self.graph_nodispatch = ProgramGraph(index, dispatch=False)
        self.namegraph = NameGraph(index)
        self.bm25 = BM25([(u.id, u.path + "\n" + u.text()) for u in index.ordered()])
        self.repo_order = [u.id for u in index.ordered()]

    # --------------------------------------------------------------- public
    def build(self, strategy, question, budget, gold_units=None):
        res = ContextResult(strategy, budget)
        if strategy == "none":
            return res
        if strategy == "oracle_trace":
            # exploratory (added post hoc): gold units + every unit executed by the oracle
            # + header units of the files involved (constants, imports)
            units = list(gold_units or [])
            files = {self.index.units[u].path for u in units}
            for path in sorted(files):
                mod = path + "::<module>"
                if mod in self.index.units and mod not in units:
                    units.append(mod)
            res.retrieved = units
            return pack(self.index, units, None, res)
        if strategy == "oracle":
            res.retrieved = list(gold_units or [])
            return pack(self.index, res.retrieved, None, res)
        if strategy == "full":
            res.retrieved = list(self.repo_order)
            return self._pack_prefix(res, budget)
        if strategy == "fixed":
            res.retrieved = [u.id for p in FIXED_FILES for u in self.index.by_path(p)]
            return self._pack_prefix(res, budget)
        if strategy == "bm25":
            res.retrieved = self.bm25.rank(question)
            return pack(self.index, res.retrieved, budget, res)
        if strategy == "bm25_namegraph":
            res.retrieved = self._bm25_namegraph(question)
            return pack(self.index, res.retrieved, budget, res)
        if strategy.startswith("dgc"):
            res.retrieved = self.dgc_rank(question, variant=strategy)
            return pack(self.index, res.retrieved, budget, res,
                        allow_skeleton=(strategy != "dgc_no_skeleton"))
        raise ValueError("unknown strategy %s" % strategy)

    # --------------------------------------------------------------- baselines
    def _pack_prefix(self, res, budget):
        """Truncation baselines: keep the given order and stop at the first unit
        that does not fit (a prefix of the ordered list, like pasting files)."""
        from ccbench import tokens
        full, files, used = [], [], 0
        for uid in res.retrieved:
            u = self.index.units[uid]
            cost = u.tokens() + 1 + (0 if u.path in files else tokens.estimate("### file: %s\n\n" % u.path))
            if budget is not None and used + cost > budget:
                break
            full.append(uid)
            used += cost
            if u.path not in files:
                files.append(u.path)
        res.full = full
        res.text = render(self.index, full, [], files)
        while budget is not None and res.est_tokens > budget and res.full:
            res.full.pop()
            res.text = render(self.index, res.full, [], files)
        return res

    def _bm25_namegraph(self, question, seeds=3, depth=2):
        ranked = self.bm25.rank(question)
        out, seen = [], set()
        frontier = ranked[:seeds]
        for s in frontier:
            if s not in seen:
                seen.add(s)
                out.append(s)
        for _ in range(depth):
            nxt = []
            for uid in frontier:
                for t in self.namegraph.callees(uid):
                    if t not in seen:
                        seen.add(t)
                        out.append(t)
                        nxt.append(t)
            frontier = nxt
        return out + [u for u in ranked if u not in seen]

    # --------------------------------------------------------------- DGC
    def seeds(self, question):
        """Seed localization: literal anchors, identifiers, file paths, BM25."""
        g, idx = self.graph, self.index
        seeds = {}

        def bump(uid, s):
            if uid in idx.units and s > seeds.get(uid, 0):
                seeds[uid] = s

        for m, path in ROUTE_PAT.findall(question):
            if (m, path) in g.routes:
                bump(g.routes[(m, path)], 1.0)
        for topic, subs in g.subscribers.items():
            if topic in question:
                for s in subs:
                    bump(s, 1.0)
        for key, units in g.config_units.items():
            if key in question:
                for u in units:
                    bump(u, 0.9)
        lowered = question.lower()
        for kind, regs in g.registry.items():
            for name, uid in regs:
                if re.search(r"['\"`]%s['\"`]" % re.escape(name), question) or re.search(
                        r"\b%s\b" % re.escape(name), lowered):
                    bump(uid, 0.7)
        names = {}
        for u in idx.units.values():
            if u.kind != "module":
                names.setdefault(u.name, []).append(u.id)
                names.setdefault(u.qualname, []).append(u.id)
        mentioned_paths = {p if p.startswith("frostline/") else "frostline/" + p for p in PATH_PAT.findall(question)}
        for a, b in IDENT_PAT.findall(question):
            tok = (a or b).strip().strip("()")
            for cand in {tok, tok.split(".")[-1], tok.split("(")[0]}:
                for uid in names.get(cand, []):
                    in_path = idx.units[uid].path in mentioned_paths
                    bump(uid, 1.0 if (in_path or not mentioned_paths) else 0.75)
        for p in mentioned_paths:
            mod = p + "::<module>"
            bump(mod, 0.6)
        scored = sorted(self.bm25.scores(question), key=lambda x: -x[0])[:5]
        top = scored[0][0] if scored and scored[0][0] > 0 else 1.0
        for s, uid in scored:
            if s > 0:
                bump(uid, 0.6 * s / top)
        return seeds

    def dgc_rank(self, question, variant="dgc"):
        graph = self.graph_nodispatch if variant == "dgc_no_dispatch" else self.graph
        seeds = self.seeds(question)
        impact = bool(IMPACT_PAT.search(question))
        use_reverse = variant != "dgc_no_reverse"
        if variant == "dgc_no_expansion":
            scores = dict(seeds)
        else:
            scores = self._expand(graph, seeds, impact, use_reverse)
        if variant == "dgc_no_ranking":
            ranked = [u for u in self.repo_order if u in scores]
        else:
            ranked = [u for u, _ in sorted(scores.items(), key=lambda kv: (-kv[1], kv[0]))]
        rest = [u for u in self.bm25.rank(question) if u not in scores]
        return ranked + rest

    def _expand(self, graph, seeds, impact, use_reverse):
        best = dict(seeds)
        heap = [(-s, uid) for uid, s in seeds.items()]
        heapq.heapify(heap)
        while heap:
            neg, uid = heapq.heappop(heap)
            score = -neg
            if score < best.get(uid, 0) - 1e-12:
                continue
            for e in graph.neighbours(uid, reverse=use_reverse):
                if e.reverse:
                    factor = 1.0 if impact else 0.45
                else:
                    factor = 0.6 if impact else 1.0
                if e.kind in ("has_member", "member_of"):
                    factor = max(factor, 0.9)
                s = score * e.weight * DECAY * factor
                if s >= MIN_SCORE and s > best.get(e.dst, 0) + 1e-12:
                    best[e.dst] = s
                    heapq.heappush(heap, (-s, e.dst))
        return best
