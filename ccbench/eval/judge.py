"""LLM-as-a-Judge for the free-text *explanation* field (secondary metric).

Primary correctness is always rule-based against executed ground truth. The
judge only rates whether the explanation is consistent with the gold answer
and gold evidence (0 = wrong/unsupported, 1 = partially, 2 = correct and
grounded). The judge model must differ from the evaluated model; agreement
with rule-based correctness is reported (Cohen's kappa) so the judge itself is
validated rather than trusted.
"""

import json
import os
import random

from ccbench.envfile import load_env
from ccbench.eval.parse import _first_object
from ccbench.providers import make_provider
from ccbench.runner import load_records

JUDGE_SYSTEM = "You are a strict grader of answers about a Python code base. Reply with JSON only."
JUDGE_TEMPLATE = """Question:
{question}

Ground-truth answer (computed by executing the code): {gold}
Code units that justify the ground truth: {units}
Reference explanation: {explanation}

Candidate answer: {pred}
Candidate explanation: {cand}

Rate the candidate EXPLANATION with this rubric:
2 = reasoning is consistent with the ground truth and names the right mechanism/code
1 = partially right (right mechanism but a wrong detail, or right answer with vague reasoning)
0 = wrong, unsupported, or contradicts the ground truth
Reply exactly as {{"score": 0|1|2, "reason": "<one sentence>"}}"""


def kappa(a, b):
    n = len(a)
    if not n:
        return None
    po = sum(1 for x, y in zip(a, b) if x == y) / n
    pa, pb = sum(a) / n, sum(b) / n
    pe = pa * pb + (1 - pa) * (1 - pb)
    return (po - pe) / (1 - pe) if pe < 1 else 1.0


def run_judge(exp_dir, provider, model, n=40, seed=1):
    load_env()
    from ccbench.dataset.build import load
    items = {i["id"]: i for i in load()}
    recs = [r for r in load_records(exp_dir) if r.get("status") == "ok" and "scores" in r]
    evaluated = {r["requested_model"] for r in recs}
    if model in evaluated:
        raise SystemExit("judge model %r is one of the evaluated models %s - choose a different judge" % (model, evaluated))
    rng = random.Random(seed)
    sample = rng.sample(recs, min(n, len(recs)))
    judge = make_provider({"provider": provider, "model": model})
    out_path = os.path.join(exp_dir, "judge_%s.jsonl" % model.replace("/", "_"))
    rows = []
    with open(out_path, "a") as fh:
        for r in sample:
            it = items[r["item_id"]]
            obj = _first_object(r["raw_response"] or "") or {}
            prompt = JUDGE_TEMPLATE.format(question=it["question"], gold=json.dumps(it["answer"]),
                                           units=", ".join(g["unit"] for g in it["gold_evidence"]),
                                           explanation=it["explanation"], pred=json.dumps(obj.get("answer")),
                                           cand=obj.get("explanation", ""))
            resp = judge.generate(JUDGE_SYSTEM, prompt, max_tokens=300)
            verdict = _first_object(resp.text or "") or {}
            row = {"job_key": r["job_key"], "item_id": r["item_id"], "model": r["model_label"], "strategy": r["strategy"],
                   "budget": r["budget"], "rule_correct": r["scores"]["correct"], "judge_model": resp.model_id,
                   "judge_score": verdict.get("score"), "judge_reason": verdict.get("reason"), "judge_cost_usd": resp.cost_usd}
            fh.write(json.dumps(row) + "\n")
            rows.append(row)
    valid = [x for x in rows if x["judge_score"] in (0, 1, 2)]
    k = kappa([1 if x["rule_correct"] else 0 for x in valid], [1 if x["judge_score"] == 2 else 0 for x in valid])
    summary = {"n": len(valid), "judge_model": model, "kappa_rule_vs_judge(score==2)": k,
               "mean_score_when_correct": _m([x["judge_score"] for x in valid if x["rule_correct"]]),
               "mean_score_when_wrong": _m([x["judge_score"] for x in valid if not x["rule_correct"]])}
    with open(os.path.join(exp_dir, "judge_summary_%s.json" % model.replace("/", "_")), "w") as fh:
        json.dump(summary, fh, indent=2)
    print(json.dumps(summary, indent=2))
    return summary


def _m(xs):
    return sum(xs) / len(xs) if xs else None
