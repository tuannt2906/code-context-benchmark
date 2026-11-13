"""Aggregate run records into metric tables and pre-registered hypothesis tests."""

import random
from collections import defaultdict

from ccbench.analysis.stats import holm, mcnemar_exact, mean, paired_bootstrap, sd, tost, wilson

LOW_BUDGETS = (2000, 4000)
HARD_LEVELS = ("L3", "L4", "L5")


def ok_records(recs):
    return [r for r in recs if r.get("status") == "ok" and "scores" in r]


def cell_key(r):
    return (r["model_label"], r["strategy"], r["budget"])


def per_item(recs, field="correct", pred=None):
    """item_id -> mean over repeats of a score field (bool -> 0/1)."""
    acc = defaultdict(list)
    for r in recs:
        if pred and not pred(r):
            continue
        v = r["scores"].get(field)
        if v is None:
            continue
        acc[r["item_id"]].append(float(v))
    return {k: mean(v) for k, v in acc.items()}


_TRACE = None


def _trace_gold():
    """item -> gold units U executed units (exploratory 'trace' evidence set)."""
    global _TRACE
    if _TRACE is None:
        from ccbench.dataset.build import load
        _TRACE = {it["id"]: set(g["unit"] for g in it["gold_evidence"]) | set(it.get("executed_units", [])) for it in load()}
    return _TRACE


def trace_recall(r):
    gold = _trace_gold().get(r["item_id"])
    if not gold:
        return None
    return len(gold & set(r["context"].get("full_units", []))) / len(gold)


def summarize(recs):
    """Return list of rows, one per (model, strategy, budget)."""
    groups = defaultdict(list)
    for r in recs:
        groups[cell_key(r)].append(r)
    rows = []
    for (model, strategy, budget), rs in sorted(groups.items(), key=lambda kv: (kv[0][0], kv[0][1], kv[0][2] or 10 ** 9)):
        ok = ok_records(rs)
        items = per_item(ok)
        n_items = len(items)
        k = sum(1 for r in ok if r["scores"]["correct"])
        n = len(ok)
        lo, hi = wilson(k, n)
        f1s = [r["scores"]["f1"] for r in ok if r["scores"].get("f1") is not None]
        corrects = [r for r in ok if r["scores"]["correct"]]
        costs = [r["cost_usd"] for r in ok if r.get("cost_usd") is not None]
        lat = [r["latency_s"] for r in ok if r.get("latency_s") is not None]
        rep_acc = defaultdict(list)
        for r in ok:
            rep_acc[r["repeat"]].append(1.0 if r["scores"]["correct"] else 0.0)
        rep_means = [mean(v) for v in rep_acc.values()]
        row = {
            "model": model, "strategy": strategy, "budget": budget if budget is not None else "unbounded",
            "n_jobs": len(rs), "n_ok": n, "n_items": n_items,
            "success_rate": sum(1 for r in ok if not r["scores"]["parse_error"]) / len(rs) if rs else float("nan"),
            "accuracy": k / n if n else float("nan"), "acc_ci_lo": lo, "acc_ci_hi": hi,
            "acc_repeat_mean": mean(rep_means), "acc_repeat_sd": sd(rep_means), "n_repeats": len(rep_means),
            "set_f1": mean(f1s) if f1s else None,
            "evidence_precision": mean(r["scores"]["evidence_precision"] for r in ok) if ok else None,
            "evidence_recall": mean(r["scores"]["evidence_recall"] for r in ok) if ok else None,
            "context_recall": mean(r["scores"]["context_recall"] for r in ok) if ok else None,
            "context_recall_soft": mean(r["scores"]["context_recall_soft"] for r in ok) if ok else None,
            "context_recall_trace": mean(x for x in (trace_recall(r) for r in ok) if x is not None) if ok else None,
            "context_est_tokens": mean(r["context"]["context_est_tokens"] for r in ok) if ok else None,
            "prompt_est_tokens": mean(r["prompt_est_tokens"] for r in ok) if ok else None,
            "input_tokens": mean(r["input_tokens"] for r in ok if r.get("input_tokens") is not None) if any(r.get("input_tokens") is not None for r in ok) else None,
            "output_tokens": mean(r["output_tokens"] for r in ok if r.get("output_tokens") is not None) if any(r.get("output_tokens") is not None for r in ok) else None,
            "latency_mean_s": mean(lat) if lat else None, "latency_sd_s": sd(lat) if lat else None,
            "cost_total_usd": sum(costs) if costs else None,
            "cost_per_task_usd": mean(costs) if costs else None,
            "cost_per_correct_usd": (sum(costs) / len(corrects)) if costs and corrects else None,
            "distractor_rate_lookalike": mean(1.0 if r["scores"]["distractor_match"] else 0.0 for r in ok if r["lookalike"]) if any(r["lookalike"] for r in ok) else None,
        }
        for lv in ("L1", "L2", "L3", "L4", "L5"):
            lv_ok = [r for r in ok if r["level"] == lv]
            row["acc_" + lv] = (sum(1 for r in lv_ok if r["scores"]["correct"]) / len(lv_ok)) if lv_ok else None
        for flag in ("indirect", "lookalike"):
            sub = [r for r in ok if r[flag]]
            row["acc_" + flag] = (sum(1 for r in sub if r["scores"]["correct"]) / len(sub)) if sub else None
        classes = defaultdict(int)
        for r in ok:
            classes[r["scores"]["error_class"]] += 1
        for c in ("correct", "distractor_confusion", "missing_evidence", "use_failure", "format_error"):
            row["n_" + c] = classes.get(c, 0)
        rows.append(row)
    return rows


def _cell(recs, model, strategy, budget, pred=None):
    return [r for r in recs if r["model_label"] == model and r["strategy"] == strategy and r["budget"] == budget
            and (pred is None or pred(r))]


def _verdict(diff, lo, hi, support_min, refute_max):
    if diff != diff:
        return "not_run"
    if diff >= support_min and lo > 0:
        return "supported"
    if hi < refute_max:
        return "refuted"
    return "inconclusive"


def hypotheses(recs, prereg):
    ok = ok_records(recs)
    models = sorted({r["model_label"] for r in ok})
    out = {}
    hard = lambda r: r["level"] in HARD_LEVELS  # noqa: E731
    for m in models:
        res, pvals = {}, {}
        # H1a: DGC - BM25 at low budgets on L3-L5
        for b in LOW_BUDGETS:
            a = per_item(_cell(ok, m, "dgc", b, hard))
            c = per_item(_cell(ok, m, "bm25", b, hard))
            if a and c:
                d, lo, hi, p = paired_bootstrap(a, c)
                mc = mcnemar_exact({k: v >= 0.5 for k, v in a.items()}, {k: v >= 0.5 for k, v in c.items()})
                res["H1a_%d" % b] = {"comparison": "dgc - bm25 @%d, L3-L5" % b, "n_items": len(set(a) & set(c)),
                                     "acc_dgc": mean(a.values()), "acc_bm25": mean(c.values()),
                                     "diff": d, "ci95": [lo, hi], "p_bootstrap": p, "mcnemar": mc,
                                     "verdict": _verdict(d, lo, hi, prereg["h1a_support"], prereg["h1a_refute"])}
                pvals["H1a_%d" % b] = p
        # H1b: gap (dgc - full) shrinks from low budget to high budget / unbounded
        dl, fl = per_item(_cell(ok, m, "dgc", 2000)), per_item(_cell(ok, m, "full", 2000))
        dh, fh = per_item(_cell(ok, m, "dgc", 16000)), per_item(_cell(ok, m, "full", None))
        keys = set(dl) & set(fl) & set(dh) & set(fh)
        if keys:
            low = {k: dl[k] - fl[k] for k in keys}
            high = {k: dh[k] - fh[k] for k in keys}
            d, lo, hi, p = paired_bootstrap(low, high)
            res["H1b"] = {"comparison": "(dgc@2K - full@2K) - (dgc@16K - full@unbounded)", "n_items": len(keys),
                          "gap_low": mean(low.values()), "gap_high": mean(high.values()), "diff": d, "ci95": [lo, hi],
                          "p_bootstrap": p, "verdict": "supported" if lo > 0 else ("refuted" if hi < 0 else "inconclusive")}
            pvals["H1b"] = p
        # H2a: accuracy conditional on full context recall, dgc vs bm25 (pooled budgets)
        def cond(strategy):
            rs = [r for r in ok if r["model_label"] == m and r["strategy"] == strategy and r["budget"] is not None]
            full = [r for r in rs if r["scores"]["context_recall"] >= 1.0]
            part = [r for r in rs if r["scores"]["context_recall"] < 1.0]
            return full, part
        fd, pd_ = cond("dgc")
        fb, pb = cond("bm25")
        if fd and fb:
            acc = lambda rs: mean(1.0 if r["scores"]["correct"] else 0.0 for r in rs) if rs else float("nan")  # noqa: E731
            diff, lo, hi = _unpaired_boot([1.0 if r["scores"]["correct"] else 0.0 for r in fd],
                                          [1.0 if r["scores"]["correct"] else 0.0 for r in fb], alpha=0.10)
            res["H2a"] = {"comparison": "acc(dgc | CR=1) - acc(bm25 | CR=1), pooled over budgets",
                          "n_dgc_cr1": len(fd), "n_bm25_cr1": len(fb), "acc_dgc_cr1": acc(fd), "acc_bm25_cr1": acc(fb),
                          "acc_dgc_cr_lt1": acc(pd_), "acc_bm25_cr_lt1": acc(pb), "diff": diff, "ci90": [lo, hi],
                          "margin": prereg["h2a_margin"],
                          "verdict": "supported (equivalent)" if (lo > -prereg["h2a_margin"] and hi < prereg["h2a_margin"]) else "not equivalent"}
        # H2b: oracle error rate on L4-L5
        orc = [r for r in ok if r["model_label"] == m and r["strategy"] == "oracle" and r["level"] in ("L4", "L5")]
        if orc:
            err = sum(1 for r in orc if not r["scores"]["correct"])
            lo, hi = wilson(err, len(orc))
            res["H2b"] = {"comparison": "oracle-context error rate, L4-L5", "n": len(orc), "error_rate": err / len(orc),
                          "ci95": [lo, hi], "threshold": prereg["h2b_error"],
                          "verdict": "supported" if (err / len(orc) >= prereg["h2b_error"] and lo > 0) else (
                              "refuted" if hi < prereg["h2b_error"] else "inconclusive")}
        # H3a: -dispatch hurts indirect items more than direct ones
        for b in prereg.get("ablation_budgets", []):
            full_i = per_item(_cell(ok, m, "dgc", b, lambda r: r["indirect"]))
            abl_i = per_item(_cell(ok, m, "dgc_no_dispatch", b, lambda r: r["indirect"]))
            full_d = per_item(_cell(ok, m, "dgc", b, lambda r: not r["indirect"]))
            abl_d = per_item(_cell(ok, m, "dgc_no_dispatch", b, lambda r: not r["indirect"]))
            if full_i and abl_i:
                di, loi, hii, pi = paired_bootstrap(full_i, abl_i)
                dd, lod, hid, _ = paired_bootstrap(full_d, abl_d) if full_d and abl_d else (float("nan"),) * 4
                res["H3a_%d" % b] = {"comparison": "dgc - dgc_no_dispatch @%d (indirect vs direct items)" % b,
                                     "diff_indirect": di, "ci95_indirect": [loi, hii], "diff_direct": dd, "ci95_direct": [lod, hid],
                                     "p_bootstrap_indirect": pi,
                                     "verdict": "supported" if (di >= prereg["h3a_support"] and loi > 0 and (dd != dd or dd < prereg["h1a_refute"])) else
                                     ("refuted" if hii < prereg["h1a_refute"] else "inconclusive")}
                pvals["H3a_%d" % b] = pi
        # H3b: distractor confusion on look-alike items, bm25 vs dgc (pooled low budgets)
        bm = {}
        dg = {}
        for b in LOW_BUDGETS:
            for r in _cell(ok, m, "bm25", b, lambda r: r["lookalike"]):
                bm[(r["item_id"], b, r["repeat"])] = bool(r["scores"]["distractor_match"])
            for r in _cell(ok, m, "dgc", b, lambda r: r["lookalike"]):
                dg[(r["item_id"], b, r["repeat"])] = bool(r["scores"]["distractor_match"])
        if bm and dg:
            n10, n01, p = mcnemar_exact(bm, dg)
            keys = set(bm) & set(dg)
            res["H3b"] = {"comparison": "distractor-confusion rate on look-alike items, bm25 vs dgc @2K+4K",
                          "rate_bm25": mean(bm[k] for k in keys), "rate_dgc": mean(dg[k] for k in keys),
                          "bm25_only": n10, "dgc_only": n01, "p_mcnemar": p,
                          "verdict": "supported" if (n10 > n01 and p < 0.05) else "inconclusive"}
            pvals["H3b"] = p
        adj = holm(pvals) if pvals else {}
        for k, v in adj.items():
            res[k]["p_holm"] = v
            if res[k].get("verdict") == "supported" and v >= 0.05:
                res[k]["verdict"] = "supported_uncorrected_only (fails Holm)"
        out[m] = res
    return out


def _unpaired_boot(a, b, n_boot=5000, seed=0, alpha=0.05):
    rng = random.Random(seed)
    obs = mean(a) - mean(b)
    boots = sorted(mean(rng.choice(a) for _ in a) - mean(rng.choice(b) for _ in b) for _ in range(n_boot))
    return obs, boots[int(alpha / 2 * n_boot)], boots[int((1 - alpha / 2) * n_boot) - 1]


def flip_rate(recs):
    """Share of (model, strategy, budget, item) cells whose correctness differs across repeats."""
    ok = ok_records(recs)
    cells = defaultdict(set)
    for r in ok:
        cells[(r["model_label"], r["strategy"], r["budget"], r["item_id"])].add(bool(r["scores"]["correct"]))
    multi = [k for k in cells if sum(1 for r in ok if (r["model_label"], r["strategy"], r["budget"], r["item_id"]) == k) > 1]
    if not multi:
        return None
    return {"n_cells_with_repeats": len(multi), "flip_rate": mean(1.0 if len(cells[k]) > 1 else 0.0 for k in multi)}


def token_calibration(recs):
    """Least squares fit provider_input_tokens = a + b * prompt_est_tokens, per model."""
    out = {}
    for m in sorted({r["model_label"] for r in recs}):
        pts = [(r["prompt_est_tokens"], r["input_tokens"]) for r in ok_records(recs)
               if r["model_label"] == m and r.get("input_tokens")]
        if len(pts) < 3:
            continue
        xs, ys = zip(*pts)
        mx, my = mean(xs), mean(ys)
        sxx = sum((x - mx) ** 2 for x in xs)
        b = sum((x - mx) * (y - my) for x, y in pts) / sxx if sxx else float("nan")
        out[m] = {"n": len(pts), "intercept_tokens": my - b * mx, "slope_actual_per_estimated": b}
    return out


def model_rank_agreement(rows):
    """Kendall tau between models over shared (strategy, budget) cells."""
    by_model = defaultdict(dict)
    for r in rows:
        by_model[r["model"]][(r["strategy"], str(r["budget"]))] = r["accuracy"]
    models = sorted(by_model)
    out = {}
    for i in range(len(models)):
        for j in range(i + 1, len(models)):
            a, b = by_model[models[i]], by_model[models[j]]
            keys = sorted(set(a) & set(b))
            conc = disc = 0
            for x in range(len(keys)):
                for y in range(x + 1, len(keys)):
                    s = (a[keys[x]] - a[keys[y]]) * (b[keys[x]] - b[keys[y]])
                    conc += s > 0
                    disc += s < 0
            out["%s vs %s" % (models[i], models[j])] = {"n_cells": len(keys),
                                                         "kendall_tau": (conc - disc) / max(1, conc + disc)}
    return out
