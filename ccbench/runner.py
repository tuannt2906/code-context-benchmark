"""Benchmark runner: expands an experiment config into jobs and executes them.

Guarantees
  * never overwrites: every run gets results/<name>-<timestamp>/ ; resume appends
  * resumable: a job whose key is already recorded with status "ok" is skipped
  * reproducible: config.json stores the full config + provenance (dataset sha,
    fixture hash, prompt version, provider effective params, versions)
  * no source dumps: records store the context *unit ids*, token counts and a
    sha of the context text, not the code itself (prompts are rebuilt on demand)
  * bounded resources: fixed worker pool, in-memory LRU for contexts, one
    temporary working directory per run that is removed at the end
"""

import datetime
import hashlib
import json
import os
import platform
import sys
import tempfile
import threading
import time
from collections import OrderedDict
from concurrent.futures import ThreadPoolExecutor, as_completed

from ccbench import PROMPT_VERSION, __version__
from ccbench.context.strategies import BUDGET_FREE, ContextBuilder
from ccbench.dataset.build import load as load_dataset
from ccbench.envfile import load_env
from ccbench.eval.prompt import SYSTEM, build_prompt, prompt_sha
from ccbench.eval.scoring import score
from ccbench.paths import FIXTURE_PKG, FIXTURE_ROOT, RESULTS_DIR, DATA_DIR
from ccbench.providers import make_provider
from ccbench.providers.base import QuotaExhausted
from ccbench.repo.index import RepoIndex
from ccbench import tokens


def expand_conditions(conditions):
    out = []
    for c in conditions:
        budgets = c.get("budgets", [c.get("budget")])
        for b in budgets:
            out.append((c["strategy"], None if c["strategy"] in BUDGET_FREE else b))
    return out


def select_items(items, sel):
    sel = sel or {}
    out = items
    if sel.get("levels"):
        out = [i for i in out if i["level"] in sel["levels"]]
    if sel.get("ids"):
        out = [i for i in out if i["id"] in sel["ids"]]
    if sel.get("limit"):
        out = out[: sel["limit"]]
    return out


def job_key(label, strategy, budget, item_id, repeat, dataset_sha):
    raw = "|".join(map(str, (label, strategy, budget, item_id, repeat, PROMPT_VERSION, dataset_sha)))
    return hashlib.sha1(raw.encode()).hexdigest()[:16]


class LRU(OrderedDict):
    def __init__(self, cap=256):
        super().__init__()
        self.cap = cap

    def get_or(self, key, fn):
        if key in self:
            self.move_to_end(key)
            return self[key]
        val = fn()
        self[key] = val
        if len(self) > self.cap:
            self.popitem(last=False)
        return val


def git_commit(path):
    try:
        import subprocess
        r = subprocess.run(["git", "-C", path, "rev-parse", "HEAD"], capture_output=True, text=True, timeout=5)
        return r.stdout.strip() or None
    except Exception:
        return None


class Runner:
    def __init__(self, config, exp_dir=None, log=print):
        load_env()
        self.config = config
        self.log = log
        self.items = select_items(load_dataset(config.get("dataset_version", "v1")), config.get("items"))
        with open(os.path.join(DATA_DIR, "manifest.%s.json" % config.get("dataset_version", "v1"))) as fh:
            self.manifest = json.load(fh)
        self.index = RepoIndex(FIXTURE_ROOT, FIXTURE_PKG)
        if self.index.content_hash() != self.manifest["fixture_hash"]:
            raise SystemExit("fixture changed since the dataset was built; run `python -m ccbench build-dataset`")
        self.builder = ContextBuilder(self.index)
        self.contexts = LRU(512)
        self.lock = threading.Lock()
        if exp_dir is None:
            stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
            exp_dir = os.path.join(RESULTS_DIR, "%s-%s" % (config["name"], stamp))
            os.makedirs(exp_dir, exist_ok=False)
        self.exp_dir = exp_dir
        self.exp_id = os.path.basename(exp_dir)
        self.results_path = os.path.join(exp_dir, "results.jsonl")

    # ------------------------------------------------------------ provenance
    def write_config(self, providers):
        snap = {
            "experiment_id": self.exp_id,
            "created": datetime.datetime.now().isoformat(timespec="seconds"),
            "config": self.config,
            "provenance": {
                "ccbench_version": __version__,
                "prompt_version": PROMPT_VERSION,
                "dataset_version": self.manifest["dataset_version"],
                "dataset_sha256": self.manifest["dataset_sha256"],
                "fixture_hash": self.manifest["fixture_hash"],
                "repo_git_commit": git_commit(os.path.dirname(FIXTURE_ROOT)),
                "chars_per_token_estimate": tokens.CHARS_PER_TOKEN,
                "python": sys.version.split()[0],
                "platform": platform.platform(),
                "providers": {label: p.effective_params() for label, p in providers.items()},
                "n_items": len(self.items),
            },
        }
        path = os.path.join(self.exp_dir, "config.json")
        if not os.path.exists(path):
            with open(path, "w") as fh:
                json.dump(snap, fh, indent=2)

    def done_keys(self):
        keys = set()
        if os.path.exists(self.results_path):
            with open(self.results_path) as fh:
                for line in fh:
                    try:
                        r = json.loads(line)
                    except ValueError:
                        continue
                    if r.get("status") == "ok":
                        keys.add(r["job_key"])
        return keys

    # ------------------------------------------------------------ execution
    def context_for(self, strategy, budget, item):
        gold = [g["unit"] for g in item["gold_evidence"]]
        if strategy == "oracle_trace":
            gold = gold + [u for u in item.get("executed_units", []) if u not in gold]
        return self.contexts.get_or((strategy, budget, item["id"]), lambda: self.builder.build(
            strategy, item["question"], budget, gold_units=gold))

    def jobs(self):
        conds = expand_conditions(self.config["conditions"])
        reps = int(self.config.get("repeats", 1))
        out = []
        # deterministic shuffle of item order: an interrupted run still covers all levels
        import random as _r
        order = sorted(self.items, key=lambda it: hashlib.sha1(("%s|%s" % (self.config.get("seed", 0), it["id"])).encode()).hexdigest())
        for item in order:
            for m in self.config["models"]:
                for strategy, budget in conds:
                    for r in range(reps):
                        out.append((m, strategy, budget, item, r))
        return out

    def run_one(self, provider, mspec, strategy, budget, item, repeat):
        key = job_key(mspec["label"], strategy, budget, item["id"], repeat, self.manifest["dataset_sha256"])
        ctx = self.context_for(strategy, budget, item)
        meta = ctx.meta()
        prompt = build_prompt(item, ctx.text)
        crecall = score(item, "", meta)["context_recall"]
        t0 = time.time()
        resp = provider.generate(SYSTEM, prompt, max_tokens=self.config.get("max_output_tokens", 1024),
                                 meta={"item": item, "context_recall": crecall, "job_key": key})
        rec = {
            "experiment_id": self.exp_id, "job_key": key,
            "timestamp": datetime.datetime.fromtimestamp(t0).isoformat(timespec="seconds"),
            "item_id": item["id"], "level": item["level"], "qtype": item["qtype"],
            "indirect": item["indirect"], "lookalike": item["lookalike"],
            "model_label": mspec["label"], "provider": mspec["provider"], "requested_model": mspec.get("model"),
            "model_id": resp.model_id, "strategy": strategy, "budget": budget, "repeat": repeat,
            "prompt_version": PROMPT_VERSION, "prompt_sha": prompt_sha(SYSTEM, prompt),
            "prompt_est_tokens": tokens.estimate(SYSTEM + prompt),
            "context": meta,
            "input_tokens": resp.input_tokens, "output_tokens": resp.output_tokens,
            "cache_read_tokens": resp.cache_read_tokens, "cache_creation_tokens": resp.cache_creation_tokens,
            "cost_usd": resp.cost_usd, "cost_source": resp.cost_source, "latency_s": resp.latency_s,
            "attempts": resp.attempts, "status": "ok" if resp.ok else "error", "error": resp.error,
            "error_kind": resp.error_kind, "provider_extra": resp.extra,
            "params": provider.effective_params(),
            "raw_response": resp.text,
            "gold_answer": item["answer"], "distractor_answer": item.get("distractor_answer"),
        }
        if resp.ok:
            rec["scores"] = score(item, resp.text, meta)
        return rec

    def run(self):
        import signal
        try:  # make SIGTERM run the cleanup in `finally` (temporary directory removal)
            signal.signal(signal.SIGTERM, lambda *a: (_ for _ in ()).throw(SystemExit(143)))
        except ValueError:
            pass  # not in the main thread (e.g. tests)
        tmp = tempfile.TemporaryDirectory(prefix="ccbench-")
        try:
            providers = {}
            for m in self.config["models"]:
                runtime = {"workdir": tmp.name} if m["provider"] == "claude_cli" else {}
                providers[m["label"]] = make_provider(m, **runtime)
            self.write_config(providers)
            done = self.done_keys()
            todo = [j for j in self.jobs()
                    if job_key(j[0]["label"], j[1], j[2], j[3]["id"], j[4], self.manifest["dataset_sha256"]) not in done]
            self.log("[%s] %d jobs total, %d already done, %d to run" % (self.exp_id, len(self.jobs()), len(done), len(todo)))
            dead = set()
            n_ok = n_err = 0
            t_start = time.time()
            with ThreadPoolExecutor(max_workers=int(self.config.get("concurrency", 2))) as pool, \
                    open(self.results_path, "a") as out:
                pending = {}
                it = iter(todo)

                def submit_next():
                    for j in it:
                        if j[0]["label"] in dead:
                            continue
                        fut = pool.submit(self.run_one, providers[j[0]["label"]], *j)
                        pending[fut] = j
                        return True
                    return False

                for _ in range(int(self.config.get("concurrency", 2)) * 2):
                    submit_next()
                while pending:
                    fut = next(as_completed(list(pending)))
                    j = pending.pop(fut)
                    try:
                        rec = fut.result()
                    except QuotaExhausted as exc:
                        dead.add(j[0]["label"])
                        self.log("!! quota exhausted for %s: %s -- stopping this model; resume later" % (j[0]["label"], exc))
                        continue
                    with self.lock:
                        out.write(json.dumps(rec) + "\n")
                        out.flush()
                    if rec["status"] == "ok":
                        n_ok += 1
                    else:
                        n_err += 1
                    total = n_ok + n_err
                    if total % 25 == 0 or not pending:
                        rate = total / max(1e-9, time.time() - t_start)
                        self.log("  %d/%d done (%d errors), %.2f jobs/s" % (total, len(todo), n_err, rate))
                    submit_next()
            self.log("[%s] finished: %d ok, %d errors -> %s" % (self.exp_id, n_ok, n_err, self.results_path))
        finally:
            tmp.cleanup()
        return self.exp_dir


def load_records(exp_dir, rescore=True):
    recs = []
    with open(os.path.join(exp_dir, "results.jsonl")) as fh:
        for line in fh:
            if line.strip():
                recs.append(json.loads(line))
    # keep the latest record per job key (a resumed run may retry failed jobs)
    latest = {}
    for r in recs:
        latest[r["job_key"]] = r
    out = list(latest.values())
    if rescore:
        # always score from the stored raw response with the current scorer (raw file untouched)
        from ccbench.dataset.build import load
        from ccbench.eval.scoring import SCORER_VERSION
        items = {i["id"]: i for i in load()}
        for r in out:
            if r.get("status") == "ok":
                r["scores"] = score(items[r["item_id"]], r["raw_response"], r["context"])
                r["scorer_version"] = SCORER_VERSION
    return out
