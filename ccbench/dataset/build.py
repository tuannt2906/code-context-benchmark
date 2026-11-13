"""Build and validate the dataset: specs + executed ground truth -> JSONL.

Validation (any failure aborts the build):
  * every oracle runs without error and produces a non-null answer
  * every gold evidence unit exists in the repository index
  * for traced items, every gold *function/method* unit was actually executed
    by the oracle (dynamic call trace), so evidence is not made up
  * the distractor answer, when defined, differs from the ground truth
  * item ids are unique
"""

import hashlib
import json
import os

from ccbench.dataset.specs import DATASET_VERSION, ITEMS
from ccbench.oracle.runner import run_oracles, trace_to_units
from ccbench.paths import DATA_DIR, FIXTURE_PKG, FIXTURE_ROOT
from ccbench.repo.index import RepoIndex


def dataset_path(version=DATASET_VERSION):
    return os.path.join(DATA_DIR, "items.%s.jsonl" % version)


def build(write=True):
    index = RepoIndex(FIXTURE_ROOT, FIXTURE_PKG)
    ids = [it["id"] for it in ITEMS]
    problems = []
    if len(ids) != len(set(ids)):
        problems.append("duplicate item ids")
    jobs = [{"id": it["id"], "oracle": it["oracle"], "distractor_oracle": it["distractor_oracle"],
             "trace": it["trace"]} for it in ITEMS]
    results = run_oracles(FIXTURE_ROOT, jobs)
    records, warnings = [], []
    for it in ITEMS:
        r = results[it["id"]]
        if r["error"] or r["answer"] is None:
            problems.append("%s: oracle failed: %s" % (it["id"], r["error"]))
            continue
        missing = [g for g in it["gold_units"] if g not in index.units]
        if missing:
            problems.append("%s: unknown gold units %s" % (it["id"], missing))
            continue
        executed = trace_to_units(index, r["trace"]) if it["trace"] else set()
        if it["trace"]:
            not_run = [g for g in it["gold_units"]
                       if index.units[g].kind in ("function", "method") and g not in executed
                       and g not in it.get("static_gold", [])]
            if not_run:
                problems.append("%s: gold units never executed by the oracle: %s" % (it["id"], not_run))
        if r["distractor"] is not None and json.dumps(r["distractor"]) == json.dumps(r["answer"]):
            warnings.append("%s: distractor equals answer" % it["id"])
        evidence = []
        for g in it["gold_units"]:
            u = index.units[g]
            evidence.append({"unit": g, "path": u.path, "start": u.start, "end": u.end, "lines": u.lines})
        rec = {k: v for k, v in it.items() if k not in ("oracle", "distractor_oracle", "trace")}
        rec["traced"] = it["trace"]
        rec.update({
            "answer": r["answer"],
            "distractor_answer": r["distractor"],
            "gold_evidence": evidence,
            "executed_units": sorted(executed),
            "oracle": it["oracle"],
            "verified_by": "execution+trace" if it["trace"] else ("mutation" if it["level"] == "L5" else "execution"),
        })
        records.append(rec)
    if problems:
        raise SystemExit("dataset validation failed:\n  " + "\n  ".join(problems))
    blob = "\n".join(json.dumps(r, sort_keys=True) for r in records) + "\n"
    manifest = {
        "dataset_version": DATASET_VERSION,
        "n_items": len(records),
        "by_level": {lv: sum(1 for r in records if r["level"] == lv) for lv in sorted({r["level"] for r in records})},
        "n_indirect": sum(r["indirect"] for r in records),
        "n_lookalike": sum(r["lookalike"] for r in records),
        "fixture_hash": index.content_hash(),
        "fixture_units": len(index.units),
        "fixture_est_tokens": index.total_tokens(),
        "dataset_sha256": hashlib.sha256(blob.encode()).hexdigest()[:16],
        "warnings": warnings,
    }
    if write:
        os.makedirs(DATA_DIR, exist_ok=True)
        with open(dataset_path(), "w") as fh:
            fh.write(blob)
        with open(os.path.join(DATA_DIR, "manifest.%s.json" % DATASET_VERSION), "w") as fh:
            json.dump(manifest, fh, indent=2)
    return records, manifest


def load(version=DATASET_VERSION):
    with open(dataset_path(version)) as fh:
        return [json.loads(line) for line in fh if line.strip()]
