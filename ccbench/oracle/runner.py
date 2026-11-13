"""Parent side of the oracle: launches the worker in an isolated subprocess."""

import json
import os
import subprocess
import sys

WORKER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "worker.py")


def run_oracles(fixture_root, jobs, timeout=300):
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
    proc = subprocess.run([sys.executable, "-I", WORKER, fixture_root], input=json.dumps(jobs),
                          capture_output=True, text=True, timeout=timeout, env=env)
    if proc.returncode != 0:
        raise RuntimeError("oracle worker failed:\n" + proc.stderr[-4000:])
    return {r["id"]: r for r in json.loads(proc.stdout)}


def trace_to_units(index, trace):
    """Map (path, co_firstlineno) pairs to unit ids (functions/methods)."""
    units = set()
    for path, first in trace:
        for u in index.units.values():
            if u.path == path and u.kind in ("function", "method") and first in (u.start, u.node.lineno):
                units.add(u.id)
    return units
