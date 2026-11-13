"""Rule-based scoring against executed ground truth (no LLM involved)."""

import json
import re
from decimal import Decimal, InvalidOperation

from ccbench.eval.parse import parse_citations, parse_response

SCORER_VERSION = "s2"  # s1: strict JSON only; s2: + recovery of answer/evidence from near-JSON
NUM = re.compile(r"-?\d+(?:\.\d+)?")


def to_number(x):
    if isinstance(x, bool) or x is None:
        return None
    if isinstance(x, (int, float)):
        return Decimal(str(x))
    if isinstance(x, str):
        s = x.replace(",", "").replace("EUR", "").replace("€", "").strip()
        try:
            return Decimal(s)
        except InvalidOperation:
            m = NUM.findall(s)
            return Decimal(m[0]) if len(m) == 1 else None
    if isinstance(x, (list, dict)):
        return None
    return None


def norm_str(x):
    if x is None:
        return ""
    if not isinstance(x, str):
        x = json.dumps(x)
    s = x.strip().strip("`'\" ").strip().lower()
    s = re.sub(r"\(\)$", "", s)
    return s


def norm_elem(x):
    s = norm_str(x)
    return s.split(".")[-1] if re.fullmatch(r"[\w.]+", s or "-") and "." in s and not NUM.fullmatch(s) else s


def as_list(x):
    if isinstance(x, list):
        return x
    if isinstance(x, str):
        s = x.strip()
        try:
            v = json.loads(s)
            if isinstance(v, list):
                return v
        except ValueError:
            pass
        return [p for p in re.split(r"[,\s]+", s) if p] if s else []
    return [x] if x is not None else []


def json_equal(a, b):
    if isinstance(a, list) and isinstance(b, list):
        return len(a) == len(b) and all(json_equal(x, y) for x, y in zip(a, b))
    if isinstance(a, dict) and isinstance(b, dict):
        return a.keys() == b.keys() and all(json_equal(a[k], b[k]) for k in a)
    na, nb = to_number(a), to_number(b)
    if na is not None and nb is not None:
        return na == nb
    return norm_str(a) == norm_str(b)


def answer_matches(atype, pred, gold):
    """-> (correct, precision, recall, f1)"""
    if atype == "number":
        p, g = to_number(pred), to_number(gold)
        ok = p is not None and g is not None and p == g
        return ok, None, None, None
    if atype == "string":
        p, g = norm_str(pred), norm_str(gold)
        ok = p == g or (p.split(".")[-1] == g and "." not in g)
        return ok, None, None, None
    if atype in ("set", "list"):
        pl = [norm_elem(x) for x in as_list(pred)]
        gl = [norm_elem(x) for x in as_list(gold)]
        ps, gs = set(pl), set(gl)
        tp = len(ps & gs)
        prec = tp / len(ps) if ps else (1.0 if not gs else 0.0)
        rec = tp / len(gs) if gs else (1.0 if not ps else 0.0)
        f1 = 2 * prec * rec / (prec + rec) if prec + rec else 0.0
        ok = (pl == gl) if atype == "list" else (ps == gs)
        return ok, prec, rec, f1
    if atype == "json":
        return json_equal(pred, gold), None, None, None
    raise ValueError(atype)


def evidence_scores(citations, gold_evidence):
    if not citations:
        return {"evidence_n": 0, "evidence_precision": 0.0, "evidence_recall": 0.0, "evidence_f1": 0.0}
    hits, covered = 0, set()
    for path, a, b in citations:
        hit = False
        for g in gold_evidence:
            if g["path"] == path and a <= g["end"] and b >= g["start"]:
                if any(a <= ln <= b for ln in g["lines"]):
                    hit = True
                    covered.add(g["unit"])
        hits += hit
    prec = hits / len(citations)
    rec = len(covered) / len(gold_evidence) if gold_evidence else 0.0
    f1 = 2 * prec * rec / (prec + rec) if prec + rec else 0.0
    return {"evidence_n": len(citations), "evidence_precision": prec, "evidence_recall": rec, "evidence_f1": f1}


def context_recall(gold_evidence, full_units, skeleton_units):
    gold = [g["unit"] for g in gold_evidence]
    if not gold:
        return 1.0, 1.0
    full, skel = set(full_units), set(skeleton_units)
    hard = sum(1 for g in gold if g in full) / len(gold)
    soft = sum(1.0 if g in full else 0.5 if g in skel else 0.0 for g in gold) / len(gold)
    return hard, soft


def score(item, raw_text, ctx_meta):
    obj, perr = parse_response(raw_text)
    out = {"parse_error": perr, "pred_answer": None, "evidence": []}
    cr, crs = context_recall(item["gold_evidence"], ctx_meta.get("full_units", []), ctx_meta.get("skeleton_units", []))
    out["context_recall"], out["context_recall_soft"] = cr, crs
    if obj is None:
        out.update({"correct": False, "precision": None, "recall": None, "f1": 0.0 if item["answer_type"] in ("set", "list") else None,
                    "distractor_match": False, "error_class": "format_error"})
        out.update(evidence_scores([], item["gold_evidence"]))
        return out
    pred = obj.get("answer")
    ok, p, r, f1 = answer_matches(item["answer_type"], pred, item["answer"])
    dm = False
    if not ok and item.get("distractor_answer") is not None:
        dm = answer_matches(item["answer_type"], pred, item["distractor_answer"])[0]
    out.update({"pred_answer": pred, "evidence": obj.get("evidence", []), "correct": ok,
                "precision": p, "recall": r, "f1": f1, "distractor_match": dm})
    out.update(evidence_scores(parse_citations(obj.get("evidence", [])), item["gold_evidence"]))
    if ok:
        cls = "correct"
    elif dm:
        cls = "distractor_confusion"
    elif cr < 1.0:
        cls = "missing_evidence"
    else:
        cls = "use_failure"
    out["error_class"] = cls
    return out
