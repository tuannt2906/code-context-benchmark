"""Write CSV/JSON tables, SVG charts and a Markdown report for one experiment."""

import csv
import json
import math
import os
import random
from collections import defaultdict

from ccbench.analysis.aggregate import flip_rate, hypotheses, model_rank_agreement, ok_records, summarize, token_calibration
from ccbench.eval.scoring import SCORER_VERSION
from ccbench.runner import load_records

# Reference categorical palette (fixed order, colour follows the entity)
SERIES = {"dgc": "#2a78d6", "bm25": "#eb6834", "bm25_namegraph": "#1baf7a", "full": "#eda100", "fixed": "#e87ba4"}
ABLATION = ["dgc", "dgc_no_dispatch", "dgc_no_expansion", "dgc_no_ranking", "dgc_no_skeleton", "dgc_no_reverse"]
ABL_COLOR = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300"]
LABEL = {"dgc": "E5 DGC (proposed)", "bm25": "E4 BM25", "bm25_namegraph": "E4b BM25+name graph",
         "full": "E2 Full (truncated)", "fixed": "E3 Fixed files", "oracle": "E0 Oracle", "none": "E1 No context",
         "oracle_trace": "E0' Trace oracle", "dgc_no_dispatch": "A1 -dispatch", "dgc_no_expansion": "A2 -expansion",
         "dgc_no_ranking": "A3 -ranking", "dgc_no_skeleton": "A4 -skeleton", "dgc_no_reverse": "A5 -reverse"}


def _legend(o, entries, x0, y, max_x, swatch="line"):
    """entries: [(label, color)]; wraps into rows. Returns the y after the legend."""
    x = x0
    for label, color in entries:
        w = 26 + 7 * len(label)
        if x + w > max_x:
            x, y = x0, y + 18
        if swatch == "line":
            o.append('<rect x="%d" y="%d" width="14" height="3" rx="1.5" fill="%s"/>' % (x, y - 4, color))
        else:
            o.append('<rect x="%d" y="%d" width="12" height="12" rx="3" fill="%s"/>' % (x, y - 10, color))
        o.append('<text x="%d" y="%d" fill="%s">%s</text>' % (x + 18, y, INK, label))
        x += w
    return y
INK, INK2, GRID, SURFACE = "#0b0b0b", "#52514e", "#e4e3df", "#fcfcfb"


def _fmt(v, nd=3):
    if v is None or (isinstance(v, float) and math.isnan(v)):
        return ""
    return round(v, nd) if isinstance(v, float) else v


def write_csv(path, rows):
    if not rows:
        return
    keys = list(rows[0].keys())
    with open(path, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=keys)
        w.writeheader()
        for r in rows:
            w.writerow({k: _fmt(r.get(k)) for k in keys})


def svg_line_chart(path, title, series, refs, xs, y_label="Accuracy"):
    """series: {name: [(x, y), ...]}; refs: {label: y} horizontal reference lines."""
    W, H, L, R, T, B = 760, 460, 64, 170, 48, 100
    pw, ph = W - L - R, H - T - B
    lx = [math.log2(x) for x in xs]
    x0, x1 = min(lx), max(lx)
    sx = lambda x: L + (math.log2(x) - x0) / (x1 - x0 or 1) * pw  # noqa: E731
    sy = lambda y: T + (1 - y) * ph  # noqa: E731
    o = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" font-family="system-ui, sans-serif" font-size="12">' % (W, H),
         '<rect width="100%%" height="100%%" fill="%s"/>' % SURFACE,
         '<text x="%d" y="24" font-size="15" font-weight="600" fill="%s">%s</text>' % (L, INK, title)]
    for t in range(0, 11, 2):
        y = sy(t / 10)
        o.append('<line x1="%d" x2="%d" y1="%.1f" y2="%.1f" stroke="%s"/>' % (L, L + pw, y, y, GRID))
        o.append('<text x="%d" y="%.1f" text-anchor="end" fill="%s">%d%%</text>' % (L - 8, y + 4, INK2, t * 10))
    for x in xs:
        o.append('<text x="%.1f" y="%d" text-anchor="middle" fill="%s">%dK</text>' % (sx(x), T + ph + 20, INK2, x // 1000))
    o.append('<text x="%d" y="%d" text-anchor="middle" fill="%s">Context budget (estimated input tokens, log scale)</text>' % (L + pw / 2, T + ph + 40, INK2))
    o.append('<text transform="translate(16,%d) rotate(-90)" text-anchor="middle" fill="%s">%s</text>' % (T + ph / 2, INK2, y_label))
    placed = []
    for i, (label, y) in enumerate(sorted(refs.items(), key=lambda kv: -(kv[1] or 0))):
        if y is None:
            continue
        ty = sy(y) + 4
        while any(abs(ty - p) < 14 for p in placed):
            ty += 14
        placed.append(ty)
        o.append('<line x1="%d" x2="%d" y1="%.1f" y2="%.1f" stroke="%s" stroke-width="1.5" stroke-dasharray="5 4"><title>%s: %.1f%%</title></line>'
                 % (L, L + pw, sy(y), sy(y), INK2, label, y * 100))
        o.append('<text x="%d" y="%.1f" fill="%s">%s %.0f%%</text>' % (L + pw + 8, ty, INK2, label, y * 100))
    entries = []
    for name, pts in series.items():
        color = SERIES.get(name, INK2)
        pts = sorted(pts)
        d = " ".join("%s%.1f %.1f" % ("M" if j == 0 else "L", sx(x), sy(y)) for j, (x, y) in enumerate(pts))
        o.append('<path d="%s" fill="none" stroke="%s" stroke-width="2"/>' % (d, color))
        for x, y in pts:
            o.append('<circle cx="%.1f" cy="%.1f" r="4.5" fill="%s" stroke="%s" stroke-width="2"><title>%s @%dK: %.1f%%</title></circle>'
                     % (sx(x), sy(y), color, SURFACE, LABEL.get(name, name), x // 1000, y * 100))
        entries.append((LABEL.get(name, name), color))
    _legend(o, entries, L, T + ph + 68, W - 10)
    o.append("</svg>")
    with open(path, "w") as fh:
        fh.write("\n".join(o))


def svg_bar_chart(path, title, groups, names, colors, y_label="Accuracy"):
    """groups: [(group_label, {name: value})] -> grouped vertical bars."""
    W, H, L, T, B = 780, 420, 60, 48, 100
    pw, ph = W - L - 20, H - T - B
    sy = lambda y: T + (1 - y) * ph  # noqa: E731
    gw = pw / max(1, len(groups))
    bw = min(22, (gw - 16) / max(1, len(names)) - 2)
    o = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" font-family="system-ui, sans-serif" font-size="12">' % (W, H),
         '<rect width="100%%" height="100%%" fill="%s"/>' % SURFACE,
         '<text x="%d" y="24" font-size="15" font-weight="600" fill="%s">%s</text>' % (L, INK, title)]
    for t in range(0, 11, 2):
        y = sy(t / 10)
        o.append('<line x1="%d" x2="%d" y1="%.1f" y2="%.1f" stroke="%s"/>' % (L, L + pw, y, y, GRID))
        o.append('<text x="%d" y="%.1f" text-anchor="end" fill="%s">%d%%</text>' % (L - 8, y + 4, INK2, t * 10))
    for gi, (glabel, vals) in enumerate(groups):
        gx = L + gi * gw + (gw - len(names) * (bw + 2)) / 2
        for ni, name in enumerate(names):
            v = vals.get(name)
            if v is None:
                continue
            x, y = gx + ni * (bw + 2), sy(v)
            h = max(0.0, T + ph - y)
            o.append('<path d="M%.1f %.1f V%.1f Q%.1f %.1f %.1f %.1f H%.1f Q%.1f %.1f %.1f %.1f V%.1f Z" fill="%s"><title>%s / %s: %.1f%%</title></path>'
                     % (x, T + ph, y + min(4, h), x, y, x + min(4, bw / 2), y, x + bw - min(4, bw / 2), x + bw, y, x + bw, y + min(4, h),
                        T + ph, colors[ni], glabel, LABEL.get(name, name), v * 100))
        o.append('<text x="%.1f" y="%d" text-anchor="middle" fill="%s">%s</text>' % (L + gi * gw + gw / 2, T + ph + 18, INK2, glabel))
    _legend(o, [(LABEL.get(n, n), colors[i]) for i, n in enumerate(names)], L, T + ph + 50, W - 10, swatch="box")
    o.append('<text transform="translate(16,%d) rotate(-90)" text-anchor="middle" fill="%s">%s</text>' % (T + ph / 2, INK2, y_label))
    o.append("</svg>")
    with open(path, "w") as fh:
        fh.write("\n".join(o))


def svg_scatter(path, title, points):
    """points: [(name, tokens, acc, label)] - accuracy vs mean input tokens."""
    W, H, L, R, T, B = 760, 460, 64, 30, 48, 100
    pw, ph = W - L - R, H - T - B
    REF = {"oracle": "#52514e", "none": "#a3a29c"}
    xs = [p[1] for p in points if p[1]]
    if not xs:
        return
    x1 = max(xs) * 1.05
    sx = lambda x: L + x / x1 * pw  # noqa: E731
    sy = lambda y: T + (1 - y) * ph  # noqa: E731
    o = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" font-family="system-ui, sans-serif" font-size="12">' % (W, H),
         '<rect width="100%%" height="100%%" fill="%s"/>' % SURFACE,
         '<text x="%d" y="24" font-size="15" font-weight="600" fill="%s">%s</text>' % (L, INK, title)]
    for t in range(0, 11, 2):
        y = sy(t / 10)
        o.append('<line x1="%d" x2="%d" y1="%.1f" y2="%.1f" stroke="%s"/>' % (L, L + pw, y, y, GRID))
        o.append('<text x="%d" y="%.1f" text-anchor="end" fill="%s">%d%%</text>' % (L - 8, y + 4, INK2, t * 10))
    step = 10 ** int(math.log10(x1)) / 2
    v = 0
    while v <= x1:
        o.append('<text x="%.1f" y="%d" text-anchor="middle" fill="%s">%.0fK</text>' % (sx(v), T + ph + 20, INK2, v / 1000))
        v += step
    o.append('<text x="%d" y="%d" text-anchor="middle" fill="%s">Mean input tokens per task (provider-reported)</text>' % (L + pw / 2, T + ph + 40, INK2))
    for name, tok, acc, lab in points:
        if tok is None:
            continue
        color = SERIES.get(name, REF.get(name, INK2))
        o.append('<circle cx="%.1f" cy="%.1f" r="5" fill="%s" stroke="%s" stroke-width="2"><title>%s: %.0f tokens, %.1f%%</title></circle>'
                 % (sx(tok), sy(acc), color, SURFACE, lab, tok, acc * 100))
    names = [n for n in SERIES if any(p[0] == n for p in points)] + [n for n in ("oracle", "none") if any(p[0] == n for p in points)]
    _legend(o, [(LABEL.get(n, n), SERIES.get(n, REF.get(n, INK2))) for n in names], L, T + ph + 68, W - 10, swatch="box")
    o.append("</svg>")
    with open(path, "w") as fh:
        fh.write("\n".join(o))


def audit_sample(recs, path, n=40, seed=7):
    """Stratified random sample for manual verification (human fills 'human_verdict')."""
    ok = ok_records(recs)
    rng = random.Random(seed)
    by = defaultdict(list)
    for r in ok:
        by[(r["level"], r["scores"]["correct"])].append(r)
    picked = []
    keys = sorted(by)
    while len(picked) < min(n, len(ok)) and keys:
        for k in list(keys):
            if by[k]:
                picked.append(by[k].pop(rng.randrange(len(by[k]))))
            else:
                keys.remove(k)
            if len(picked) >= n:
                break
    rows = [{"job_key": r["job_key"], "item_id": r["item_id"], "model": r["model_label"], "strategy": r["strategy"],
             "budget": r["budget"], "gold_answer": json.dumps(r["gold_answer"]), "pred_answer": json.dumps(r["scores"]["pred_answer"]),
             "auto_correct": r["scores"]["correct"], "auto_error_class": r["scores"]["error_class"],
             "raw_response": (r["raw_response"] or "")[:600], "human_verdict": "", "human_note": ""} for r in picked]
    write_csv(path, rows)


def build_report(exp_dir, prereg):
    recs = load_records(exp_dir)
    out_dir = os.path.join(exp_dir, "report")
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(exp_dir, "config.json")) as fh:
        cfg = json.load(fh)
    rows = summarize(recs)
    hyp = hypotheses(recs, prereg)
    extra = {"flip_rate": flip_rate(recs), "token_calibration": token_calibration(recs),
             "model_rank_agreement": model_rank_agreement(rows),
             "n_records": len(recs), "n_ok": len(ok_records(recs)),
             "n_errors": sum(1 for r in recs if r.get("status") != "ok")}
    write_csv(os.path.join(out_dir, "summary.csv"), rows)
    with open(os.path.join(out_dir, "summary.json"), "w") as fh:
        json.dump({"experiment": cfg["experiment_id"], "provenance": cfg["provenance"], "cells": rows,
                   "hypotheses": hyp, "extra": extra, "prereg": prereg}, fh, indent=2, default=str)
    audit_sample(recs, os.path.join(out_dir, "manual_audit_sample.csv"))
    charts = []
    for model in sorted({r["model"] for r in rows}):
        mr = [r for r in rows if r["model"] == model]
        budgets = sorted({r["budget"] for r in mr if isinstance(r["budget"], int)})
        series = {}
        for s in ("dgc", "bm25", "bm25_namegraph", "full", "fixed"):
            pts = [(r["budget"], r["accuracy"]) for r in mr if r["strategy"] == s and isinstance(r["budget"], int)]
            if pts:
                series[s] = pts
        refs = {}
        for s, lab in (("oracle", "E0 Oracle"), ("none", "E1 None")):
            v = [r["accuracy"] for r in mr if r["strategy"] == s]
            refs[lab] = v[0] if v else None
        v = [r["accuracy"] for r in mr if r["strategy"] == "full" and r["budget"] == "unbounded"]
        refs["E2 Full (whole repo)"] = v[0] if v else None
        safe = model.replace("/", "_")
        if budgets and series:
            p = "accuracy_vs_budget_%s.svg" % safe
            svg_line_chart(os.path.join(out_dir, p), "Accuracy vs context budget - %s (n=%d items)" % (model, max(r["n_items"] for r in mr)),
                           series, refs, budgets)
            charts.append(p)
            # hard items only
            hard_series = {}
            for s in series:
                pts = []
                for b in budgets:
                    rs = [x for x in recs if x.get("status") == "ok" and x["model_label"] == model and x["strategy"] == s
                          and x["budget"] == b and x["level"] in ("L3", "L4", "L5")]
                    if rs:
                        pts.append((b, sum(1 for x in rs if x["scores"]["correct"]) / len(rs)))
                hard_series[s] = pts
            p = "accuracy_vs_budget_L3-L5_%s.svg" % safe
            svg_line_chart(os.path.join(out_dir, p), "L3-L5 accuracy vs context budget - %s" % model, hard_series, {}, budgets)
            charts.append(p)
            # per level at 4K
            ref_b = 4000 if 4000 in budgets else budgets[0]
            names = [s for s in ("dgc", "bm25", "bm25_namegraph", "full", "fixed") if any(r["strategy"] == s and r["budget"] == ref_b for r in mr)]
            groups = []
            for lv in ("L1", "L2", "L3", "L4", "L5"):
                groups.append((lv, {s: next((r["acc_" + lv] for r in mr if r["strategy"] == s and r["budget"] == ref_b), None) for s in names}))
            p = "accuracy_by_level_%dK_%s.svg" % (ref_b // 1000, safe)
            svg_bar_chart(os.path.join(out_dir, p), "Accuracy by difficulty level at %dK budget - %s" % (ref_b // 1000, model),
                          groups, names, [SERIES[s] for s in names])
            charts.append(p)
        abl = [s for s in ABLATION if any(r["strategy"] == s for r in mr)]
        if len(abl) > 1:
            abl_budgets = sorted({r["budget"] for r in mr if r["strategy"] == "dgc_no_dispatch" and isinstance(r["budget"], int)})
            groups = []
            for b in abl_budgets:
                for flag, lab in (("acc_indirect", "indirect"), ("accuracy", "all")):
                    groups.append(("%dK %s" % (b // 1000, lab), {s: next((r[flag] for r in mr if r["strategy"] == s and r["budget"] == b), None) for s in abl}))
            p = "ablation_%s.svg" % safe
            svg_bar_chart(os.path.join(out_dir, p), "DGC ablation - %s" % model, groups, abl, ABL_COLOR[:len(abl)])
            charts.append(p)
        pts = [(r["strategy"], r["input_tokens"], r["accuracy"], "%s %s" % (LABEL.get(r["strategy"], r["strategy"]), r["budget"]))
               for r in mr if r["strategy"] in list(SERIES) + ["oracle", "none"]]
        if any(p[1] for p in pts):
            p = "accuracy_vs_tokens_%s.svg" % safe
            svg_scatter(os.path.join(out_dir, p), "Accuracy vs input tokens - %s" % model, pts)
            charts.append(p)
    md = render_markdown(cfg, rows, hyp, extra, charts)
    with open(os.path.join(out_dir, "report.md"), "w") as fh:
        fh.write(md)
    return out_dir


def _pct(v):
    return "" if v is None or (isinstance(v, float) and math.isnan(v)) else "%.1f" % (100 * v)


def render_markdown(cfg, rows, hyp, extra, charts):
    prov = cfg["provenance"]
    simulated = any(p.get("model", "").startswith("mock") for p in prov["providers"].values()) or \
        any(m["provider"] == "mock" for m in cfg["config"]["models"])
    L = ["# Results - %s" % cfg["experiment_id"], ""]
    if simulated:
        L += ["> **SIMULATED RUN (mock provider).** Numbers below test the pipeline only; they are NOT experimental results.", ""]
    L += ["- Created: %s; dataset %s (sha %s); fixture %s; prompt %s; ccbench %s" % (
        cfg["created"], prov["dataset_version"], prov["dataset_sha256"], prov["fixture_hash"], prov["prompt_version"], prov["ccbench_version"]),
          "- Providers (effective parameters): `%s`" % json.dumps(prov["providers"]),
          "- Records: %d (ok %d, errors %d); scored from raw responses with scorer %s" % (extra["n_records"], extra["n_ok"], extra["n_errors"], SCORER_VERSION), ""]
    L += ["## Accuracy and cost per condition", "",
          "| model | strategy | budget | n | acc % [95% CI] | L1 | L2 | L3 | L4 | L5 | ctx recall | evid. P | evid. R | est ctx tok | input tok | out tok | latency s | cost/task $ |",
          "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for r in rows:
        L.append("| %s | %s | %s | %d | %s [%s, %s] | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s |" % (
            r["model"], r["strategy"], r["budget"], r["n_ok"], _pct(r["accuracy"]), _pct(r["acc_ci_lo"]), _pct(r["acc_ci_hi"]),
            _pct(r["acc_L1"]), _pct(r["acc_L2"]), _pct(r["acc_L3"]), _pct(r["acc_L4"]), _pct(r["acc_L5"]),
            _pct(r["context_recall"]), _pct(r["evidence_precision"]), _pct(r["evidence_recall"]),
            "%.0f" % r["context_est_tokens"] if r["context_est_tokens"] is not None else "",
            "%.0f" % r["input_tokens"] if r["input_tokens"] else "", "%.0f" % r["output_tokens"] if r["output_tokens"] else "",
            "%.1f" % r["latency_mean_s"] if r["latency_mean_s"] else "", "%.4f" % r["cost_per_task_usd"] if r["cost_per_task_usd"] else ""))
    L += ["", "## Pre-registered hypotheses", ""]
    for model, res in hyp.items():
        L.append("### %s" % model)
        L.append("")
        for k, v in res.items():
            L.append("- **%s** - %s: `%s`" % (k, v.get("verdict"), json.dumps({kk: (round(vv, 4) if isinstance(vv, float) else vv) for kk, vv in v.items() if kk != "verdict"}, default=str)))
        L.append("")
    L += ["## Other diagnostics", "", "```json", json.dumps(extra, indent=2, default=str), "```", "", "## Charts", ""]
    L += ["![%s](%s)" % (c, c) for c in charts]
    return "\n".join(L) + "\n"
