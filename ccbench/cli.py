"""Command line interface: python -m ccbench <command> ..."""

import argparse
import json
import os
import shutil
import sys

from ccbench.paths import CONFIG_DIR, DATA_DIR, FIXTURE_PKG, FIXTURE_ROOT, RESULTS_DIR


def _prereg():
    with open(os.path.join(CONFIG_DIR, "prereg.json")) as fh:
        return json.load(fh)


def cmd_build(args):
    from ccbench.dataset.build import build
    recs, man = build(write=not args.check)
    print(json.dumps(man, indent=2))
    if args.check:
        with open(os.path.join(DATA_DIR, "manifest.%s.json" % man["dataset_version"])) as fh:
            saved = json.load(fh)
        same = saved["dataset_sha256"] == man["dataset_sha256"]
        print("ground truth reproduced exactly" if same else "MISMATCH with saved dataset")
        sys.exit(0 if same else 1)


def cmd_context_stats(args):
    """Offline (no model): context recall / tokens per strategy x budget."""
    from ccbench.analysis.stats import mean
    from ccbench.context.strategies import ContextBuilder
    from ccbench.dataset.build import load
    from ccbench.eval.scoring import context_recall
    from ccbench.repo.index import RepoIndex
    from ccbench.runner import expand_conditions
    index = RepoIndex(FIXTURE_ROOT, FIXTURE_PKG)
    b = ContextBuilder(index)
    items = load()
    with open(args.config) as fh:
        cfg = json.load(fh)
    rows = []
    for strategy, budget in expand_conditions(cfg["conditions"]):
        crs, soft, toks, hard = [], [], [], []
        for it in items:
            ctx = b.build(strategy, it["question"], budget, [g["unit"] for g in it["gold_evidence"]])
            cr, crs_ = context_recall(it["gold_evidence"], ctx.full, ctx.skeleton)
            crs.append(cr); soft.append(crs_); toks.append(ctx.est_tokens)
            if it["level"] in ("L3", "L4", "L5"):
                hard.append(cr)
        rows.append({"strategy": strategy, "budget": budget, "context_recall": mean(crs), "context_recall_soft": mean(soft),
                     "context_recall_L3_L5": mean(hard), "full_recall_rate": mean(1.0 if c >= 1 else 0.0 for c in crs),
                     "est_tokens": mean(toks)})
    print("%-18s %8s %8s %8s %8s %8s %8s" % ("strategy", "budget", "CR", "CRsoft", "CR_L3-5", "CR=1", "tokens"))
    for r in rows:
        print("%-18s %8s %8.3f %8.3f %8.3f %8.3f %8.0f" % (r["strategy"], r["budget"], r["context_recall"], r["context_recall_soft"],
                                                         r["context_recall_L3_L5"], r["full_recall_rate"], r["est_tokens"]))
    if args.out:
        with open(args.out, "w") as fh:
            json.dump(rows, fh, indent=2)


def cmd_show_context(args):
    from ccbench.context.strategies import ContextBuilder
    from ccbench.dataset.build import load
    from ccbench.eval.prompt import SYSTEM, build_prompt
    from ccbench.repo.index import RepoIndex
    index = RepoIndex(FIXTURE_ROOT, FIXTURE_PKG)
    it = next(i for i in load() if i["id"] == args.item)
    budget = None if args.budget in (None, 0) else args.budget
    ctx = ContextBuilder(index).build(args.strategy, it["question"], budget, [g["unit"] for g in it["gold_evidence"]])
    print(json.dumps({k: v for k, v in ctx.meta().items() if not k.endswith("_units")}, indent=2))
    print("gold units:", [g["unit"] for g in it["gold_evidence"]])
    print("missing   :", [g["unit"] for g in it["gold_evidence"] if g["unit"] not in ctx.full])
    if args.prompt:
        print(SYSTEM)
        print(build_prompt(it, ctx.text))


def cmd_run(args):
    from ccbench.runner import Runner
    with open(args.config) as fh:
        cfg = json.load(fh)
    if "config" in cfg and "provenance" in cfg:  # re-run from a saved experiment config
        cfg = cfg["config"]
    if args.limit:
        cfg.setdefault("items", {})["limit"] = args.limit
    if args.concurrency:
        cfg["concurrency"] = args.concurrency
    exp = Runner(cfg).run()
    if not args.no_report:
        from ccbench.report.report import build_report
        print("report:", build_report(exp, _prereg()))


def cmd_resume(args):
    from ccbench.runner import Runner
    with open(os.path.join(args.exp_dir, "config.json")) as fh:
        cfg = json.load(fh)["config"]
    exp = Runner(cfg, exp_dir=args.exp_dir).run()
    from ccbench.report.report import build_report
    print("report:", build_report(exp, _prereg()))


def cmd_rescore(args):
    """Re-score raw responses with the current scorer (results file rewritten to results.rescored.jsonl)."""
    from ccbench.dataset.build import load
    from ccbench.eval.scoring import score
    items = {i["id"]: i for i in load()}
    src = os.path.join(args.exp_dir, "results.jsonl")
    dst = os.path.join(args.exp_dir, "results.rescored.jsonl")
    n = 0
    with open(src) as fh, open(dst, "w") as out:
        for line in fh:
            r = json.loads(line)
            if r.get("status") == "ok":
                r["scores"] = score(items[r["item_id"]], r["raw_response"], r["context"])
                n += 1
            out.write(json.dumps(r) + "\n")
    print("rescored %d records -> %s" % (n, dst))


def cmd_report(args):
    from ccbench.report.report import build_report
    print(build_report(args.exp_dir, _prereg()))


def cmd_combine(args):
    """Concatenate several experiment result files into one directory for joint analysis."""
    os.makedirs(args.out, exist_ok=False)
    first = None
    with open(os.path.join(args.out, "results.jsonl"), "w") as out:
        for d in args.exp_dirs:
            with open(os.path.join(d, "results.jsonl")) as fh:
                shutil.copyfileobj(fh, out)
            if first is None:
                first = d
    with open(os.path.join(first, "config.json")) as fh:
        cfg = json.load(fh)
    cfg["experiment_id"] = os.path.basename(args.out)
    cfg["combined_from"] = [os.path.basename(d) for d in args.exp_dirs]
    providers = {}
    for d in args.exp_dirs:
        with open(os.path.join(d, "config.json")) as fh:
            providers.update(json.load(fh)["provenance"]["providers"])
    cfg["provenance"]["providers"] = providers
    with open(os.path.join(args.out, "config.json"), "w") as fh:
        json.dump(cfg, fh, indent=2)
    from ccbench.report.report import build_report
    print(build_report(args.out, _prereg()))


def cmd_judge(args):
    from ccbench.eval.judge import run_judge
    run_judge(args.exp_dir, args.judge_provider, args.judge_model, args.n, args.seed)


def cmd_clean(args):
    """Remove caches. Results are kept unless --results is given explicitly."""
    removed = 0
    for root, dirs, _ in os.walk(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))):
        for d in list(dirs):
            if d == "__pycache__":
                shutil.rmtree(os.path.join(root, d), ignore_errors=True)
                removed += 1
    print("removed %d __pycache__ dirs" % removed)
    if args.results:
        for d in args.results:
            p = os.path.join(RESULTS_DIR, d)
            if os.path.isdir(p) and os.path.abspath(p).startswith(os.path.abspath(RESULTS_DIR)):
                shutil.rmtree(p)
                print("removed", p)


def main(argv=None):
    sys.dont_write_bytecode = True
    p = argparse.ArgumentParser(prog="ccbench")
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("build-dataset"); s.add_argument("--check", action="store_true"); s.set_defaults(f=cmd_build)
    s = sub.add_parser("context-stats"); s.add_argument("--config", default=os.path.join(CONFIG_DIR, "main_haiku.json")); s.add_argument("--out"); s.set_defaults(f=cmd_context_stats)
    s = sub.add_parser("show-context"); s.add_argument("item"); s.add_argument("strategy"); s.add_argument("--budget", type=int, default=4000)
    s.add_argument("--prompt", action="store_true"); s.set_defaults(f=cmd_show_context)
    s = sub.add_parser("run"); s.add_argument("config"); s.add_argument("--limit", type=int); s.add_argument("--concurrency", type=int)
    s.add_argument("--no-report", action="store_true"); s.set_defaults(f=cmd_run)
    s = sub.add_parser("resume"); s.add_argument("exp_dir"); s.set_defaults(f=cmd_resume)
    s = sub.add_parser("rescore"); s.add_argument("exp_dir"); s.set_defaults(f=cmd_rescore)
    s = sub.add_parser("report"); s.add_argument("exp_dir"); s.set_defaults(f=cmd_report)
    s = sub.add_parser("combine"); s.add_argument("out"); s.add_argument("exp_dirs", nargs="+"); s.set_defaults(f=cmd_combine)
    s = sub.add_parser("judge"); s.add_argument("exp_dir"); s.add_argument("--judge-provider", default="claude_cli")
    s.add_argument("--judge-model", default="sonnet"); s.add_argument("--n", type=int, default=40); s.add_argument("--seed", type=int, default=1)
    s.set_defaults(f=cmd_judge)
    s = sub.add_parser("clean"); s.add_argument("--results", nargs="*"); s.set_defaults(f=cmd_clean)
    args = p.parse_args(argv)
    args.f(args)


if __name__ == "__main__":
    main()
