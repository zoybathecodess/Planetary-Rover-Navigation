"""Statistics for the study (pure numpy/math: no SciPy dependency). Evaluation side only.

* t-based confidence intervals over system seeds (the unit of replication for learned methods)
* Wilson interval for proportions (deterministic methods / pooled counts)
* paired comparison over seeds: mean difference, t interval, EXACT sign-flip permutation p-value (2^n flips; n <= 20)
* Holm-Bonferroni step-down adjustment
"""
from __future__ import annotations

import itertools
import math

import numpy as np


def _betacf(a: float, b: float, x: float, itmax: int = 400, eps: float = 3e-14) -> float:
    qab, qap, qam = a + b, a + 1.0, a - 1.0
    c, d = 1.0, 1.0 - qab * x / qap
    d = 1.0 / (d if abs(d) > 1e-300 else 1e-300)
    h = d
    for m in range(1, itmax + 1):
        m2 = 2 * m
        aa = m * (b - m) * x / ((qam + m2) * (a + m2))
        d = 1.0 + aa * d; d = d if abs(d) > 1e-300 else 1e-300
        c = 1.0 + aa / c; c = c if abs(c) > 1e-300 else 1e-300
        d = 1.0 / d; h *= d * c
        aa = -(a + m) * (qab + m) * x / ((a + m2) * (qap + m2))
        d = 1.0 + aa * d; d = d if abs(d) > 1e-300 else 1e-300
        c = 1.0 + aa / c; c = c if abs(c) > 1e-300 else 1e-300
        d = 1.0 / d; delta = d * c; h *= delta
        if abs(delta - 1.0) < eps:
            break
    return h


def betainc(a: float, b: float, x: float) -> float:
    """Regularised incomplete beta I_x(a, b)."""
    if x <= 0.0:
        return 0.0
    if x >= 1.0:
        return 1.0
    bt = math.exp(math.lgamma(a + b) - math.lgamma(a) - math.lgamma(b) + a * math.log(x) + b * math.log1p(-x))
    if x < (a + 1.0) / (a + b + 2.0):
        return bt * _betacf(a, b, x) / a
    return 1.0 - bt * _betacf(b, a, 1.0 - x) / b


def t_two_sided_p(t: float, df: int) -> float:
    return betainc(df / 2.0, 0.5, df / (df + t * t))


def t_crit(df: int, conf: float = 0.95) -> float:
    """Two-sided critical value t_{1-(1-conf)/2, df}."""
    if df < 1:
        return float("nan")
    alpha, lo, hi = 1.0 - conf, 0.0, 1e4
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        if t_two_sided_p(mid, df) > alpha:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def mean_ci(values, conf: float = 0.95) -> dict:
    v = np.asarray([x for x in values if not (x is None or (isinstance(x, float) and math.isnan(x)))], float)
    n = len(v)
    if n == 0:
        return {"n": 0, "mean": float("nan"), "sd": float("nan"), "lo": float("nan"), "hi": float("nan")}
    m = float(v.mean())
    if n < 2:
        return {"n": n, "mean": m, "sd": float("nan"), "lo": float("nan"), "hi": float("nan")}
    sd = float(v.std(ddof=1)); h = t_crit(n - 1, conf) * sd / math.sqrt(n)
    return {"n": n, "mean": m, "sd": sd, "lo": m - h, "hi": m + h}


def wilson(k: int, n: int, conf: float = 0.95) -> tuple[float, float]:
    if n == 0:
        return float("nan"), float("nan")
    z = _z(conf)
    p = k / n
    den = 1 + z * z / n
    c = (p + z * z / (2 * n)) / den
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return max(0.0, c - h), min(1.0, c + h)


def _z(conf: float) -> float:
    from statistics import NormalDist
    return NormalDist().inv_cdf(0.5 + conf / 2)


def sign_flip_p(diffs) -> float:
    """Exact two-sided paired permutation (sign-flip) p-value for H0: symmetric about 0. Needs n <= 20 non-zero pairs."""
    d = np.asarray([x for x in diffs if x == x and x != 0.0], float)
    n = len(d)
    if n == 0:
        return 1.0
    if n > 20:
        raise ValueError("exact sign-flip test limited to 20 non-zero pairs; use the t-based p-value")
    obs = abs(d.sum())
    signs = np.array(list(itertools.product((-1.0, 1.0), repeat=n)))
    return float((np.abs(signs @ d) >= obs - 1e-12).mean())


def paired_diff(a, b, conf: float = 0.95) -> dict:
    """a, b: equal-length sequences paired by system seed. Returns mean(a-b), t interval, t p-value, exact sign-flip p."""
    a, b = np.asarray(a, float), np.asarray(b, float)
    keep = ~(np.isnan(a) | np.isnan(b))
    d = (a - b)[keep]
    n = len(d)
    out = {"n": n, "mean_diff": float(d.mean()) if n else float("nan"), "lo": float("nan"), "hi": float("nan"),
           "p_t": float("nan"), "p_perm": float("nan")}
    if n >= 2:
        sd = float(d.std(ddof=1)); se = sd / math.sqrt(n)
        h = t_crit(n - 1, conf) * se
        out["lo"], out["hi"] = out["mean_diff"] - h, out["mean_diff"] + h
        out["p_t"] = 1.0 if (sd == 0 and out["mean_diff"] == 0) else (0.0 if sd == 0 else t_two_sided_p(out["mean_diff"] / se, n - 1))
        out["p_perm"] = sign_flip_p(d)
    return out


def holm(pvals) -> list[float]:
    """Holm step-down adjusted p-values (same order as input; NaN stays NaN)."""
    p = np.asarray(pvals, float)
    idx = [i for i in range(len(p)) if not math.isnan(p[i])]
    order = sorted(idx, key=lambda i: p[i])
    m, adj, run = len(order), np.full(len(p), np.nan), 0.0
    for rank, i in enumerate(order):
        run = max(run, min(1.0, (m - rank) * p[i]))
        adj[i] = run
    return adj.tolist()
