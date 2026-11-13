"""Oracle worker: executes item oracles against the fixture in a subprocess.

Usage: python -I worker.py <fixture_root>   (JSON list of jobs on stdin)
Each job: {"id", "oracle", "distractor_oracle", "trace"}.
Output: JSON list of {"id", "answer", "distractor", "trace", "error"}.

Mutations for impact analysis are applied in-process by swapping function
objects (module globals, class attributes, and module-level containers that
hold references, e.g. event subscriber lists). No source file is copied or
modified on disk.
"""

import copy
import functools
import importlib
import json
import os
import sys
import traceback
from decimal import Decimal


def jsonable(x):
    if isinstance(x, Decimal):
        return str(x)
    if isinstance(x, (list, tuple)):
        return [jsonable(v) for v in x]
    if isinstance(x, dict):
        return {str(k): jsonable(v) for k, v in x.items()}
    if isinstance(x, (set, frozenset)):
        return sorted(jsonable(v) for v in x)
    return x


def main():
    root = os.path.abspath(sys.argv[1])
    sys.path.insert(0, root)
    sys.dont_write_bytecode = True
    import frostline.api.app as appmod  # noqa: F401  (registers everything)
    from frostline.api.app import App

    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    from ccbench.dataset.scenarios import SCENARIOS

    pkg_dir = os.path.join(root, "frostline") + os.sep

    def app(profile="default", overrides=None):
        return App(profile, overrides)

    def call(a, method, path, body):
        r = a.handle(method, path, copy.deepcopy(body))
        if r["status"] != 200:
            raise RuntimeError("request failed: %r" % r)
        return r["body"]

    def scenario(sid):
        sc = SCENARIOS[sid]
        a = app(sc["profile"])
        out = []
        for m, p, b in sc["requests"]:
            r = jsonable(a.handle(m, p, copy.deepcopy(b)))
            out.append(r["body"] if r["status"] == 200 else r)
        return out

    def transform(kind):
        def outer(orig):
            @functools.wraps(orig)
            def wrapper(*a, **k):
                if kind == "empty_list":
                    return []
                r = orig(*a, **k)
                if kind == "plus_cent":
                    return r + Decimal("0.01")
                if kind == "plus_one":
                    return r + 1
                if kind == "reverse_list":
                    return list(reversed(r))
                if kind == "lower":
                    return r.lower()
                raise ValueError(kind)
            return wrapper
        return outer

    def apply_mutation(target, kind):
        modname, attr = target.split(":")
        mod = importlib.import_module(modname)
        undo = []
        if "." in attr:
            cls_name, meth = attr.split(".")
            owner = getattr(mod, cls_name)
            orig = owner.__dict__[meth]
            setattr(owner, meth, transform(kind)(orig))
            undo.append(lambda: setattr(owner, meth, orig))
            return undo
        orig = getattr(mod, attr)
        new = transform(kind)(orig)
        for m in list(sys.modules.values()):
            if not getattr(m, "__name__", "").startswith("frostline"):
                continue
            for name, val in list(vars(m).items()):
                if val is orig:
                    setattr(m, name, new)
                    undo.append(functools.partial(setattr, m, name, orig))
                elif isinstance(val, dict):
                    for k, v in list(val.items()):
                        if v is orig:
                            val[k] = new
                            undo.append(functools.partial(val.__setitem__, k, orig))
                        elif isinstance(v, list):
                            for i, e in enumerate(v):
                                if e is orig:
                                    v[i] = new
                                    undo.append(functools.partial(v.__setitem__, i, orig))
                elif isinstance(val, list):
                    for i, e in enumerate(val):
                        if e is orig:
                            val[i] = new
                            undo.append(functools.partial(val.__setitem__, i, orig))
        return undo

    def snapshot():
        return {sid: json.dumps(scenario(sid), sort_keys=True) for sid in sorted(SCENARIOS)}

    baseline = {}

    def impact(target, kind):
        if not baseline:
            baseline.update(snapshot())
        undo = apply_mutation(target, kind)
        try:
            mutated = snapshot()
        finally:
            for u in reversed(undo):
                u()
        assert snapshot() == baseline, "mutation was not undone cleanly"
        return sorted(sid for sid in baseline if baseline[sid] != mutated[sid])

    jobs = json.load(sys.stdin)
    out = []
    for job in jobs:
        rec = {"id": job["id"], "answer": None, "distractor": None, "trace": [], "error": None}
        env = {"D": Decimal, "app": app, "call": call, "scenario": scenario, "impact": impact}
        calls = set()

        def prof(frame, event, arg):
            if event == "call":
                fn = frame.f_code.co_filename
                if fn.startswith(pkg_dir):
                    calls.add((os.path.relpath(fn, root).replace(os.sep, "/"), frame.f_code.co_firstlineno))

        try:
            if job.get("trace"):
                sys.setprofile(prof)
            try:
                exec(job["oracle"], env)
            finally:
                sys.setprofile(None)
            rec["answer"] = jsonable(env.get("ANSWER"))
            if job.get("distractor_oracle"):
                exec(job["distractor_oracle"], env)
            if "DISTRACTOR" in env:
                rec["distractor"] = jsonable(env["DISTRACTOR"])
            rec["trace"] = sorted(calls)
        except Exception:
            rec["error"] = traceback.format_exc(limit=3)
        out.append(rec)
    json.dump(out, sys.stdout)


if __name__ == "__main__":
    main()
