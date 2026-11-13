"""Statistics (stdlib only): Wilson CI, paired bootstrap, exact McNemar, Holm, TOST."""

import math
import random


def mean(xs):
    xs = list(xs)
    return sum(xs) / len(xs) if xs else float("nan")


def sd(xs):
    xs = list(xs)
    if len(xs) < 2:
        return 0.0
    m = mean(xs)
    return math.sqrt(sum((x - m) ** 2 for x in xs) / (len(xs) - 1))


def wilson(k, n, z=1.96):
    if n == 0:
        return (float("nan"), float("nan"))
    p = k / n
    d = 1 + z * z / n
    c = p + z * z / (2 * n)
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return ((c - h) / d, (c + h) / d)


def paired_bootstrap(a, b, n_boot=10000, seed=0, alpha=0.05):
    """a, b: dicts item -> score in [0,1]; difference mean(a-b) over shared items.
    Returns (diff, lo, hi, p_two_sided) with percentile CI and bootstrap p."""
    keys = sorted(set(a) & set(b))
    if not keys:
        return (float("nan"),) * 4
    d = [a[k] - b[k] for k in keys]
    obs = mean(d)
    rng = random.Random(seed)
    n = len(d)
    boots = []
    for _ in range(n_boot):
        boots.append(sum(d[rng.randrange(n)] for _ in range(n)) / n)
    boots.sort()
    lo = boots[int(alpha / 2 * n_boot)]
    hi = boots[int((1 - alpha / 2) * n_boot) - 1]
    # two-sided p: proportion of centred bootstrap stats at least as extreme
    p = sum(1 for x in boots if abs(x - obs) >= abs(obs)) / n_boot if obs != 0 else 1.0
    return obs, lo, hi, max(p, 1.0 / n_boot)


def mcnemar_exact(a, b):
    """a, b: dicts item -> bool. Returns (b_only, a_only, p)."""
    keys = sorted(set(a) & set(b))
    n01 = sum(1 for k in keys if not a[k] and b[k])
    n10 = sum(1 for k in keys if a[k] and not b[k])
    n = n01 + n10
    if n == 0:
        return n10, n01, 1.0
    k = min(n01, n10)
    p = sum(math.comb(n, i) for i in range(0, k + 1)) / 2 ** n * 2
    return n10, n01, min(1.0, p)


def holm(pvals):
    """pvals: dict name -> p. Returns dict name -> adjusted p."""
    items = sorted(pvals.items(), key=lambda kv: kv[1])
    m = len(items)
    adj, running = {}, 0.0
    for i, (name, p) in enumerate(items):
        running = max(running, min(1.0, (m - i) * p))
        adj[name] = running
    return adj


def tost(a, b, margin, n_boot=10000, seed=0):
    """Equivalence via 90% paired bootstrap CI inside [-margin, margin]."""
    diff, lo, hi, _ = paired_bootstrap(a, b, n_boot=n_boot, seed=seed, alpha=0.10)
    return {"diff": diff, "ci90": [lo, hi], "margin": margin, "equivalent": (lo > -margin and hi < margin)}
