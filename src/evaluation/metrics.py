"""Per-(method, system seed, condition) metrics from episode rows, and loading of a run directory. Evaluation side only.

Metric definitions (all computed over the SAME maps for every method):
  success            fraction of episodes ending with reason == goal  (a safe stop is a failure of the mission)
  collisions         mean collisions per episode                          unsafe  mean attempted unsafe commands per episode
  steps_goal         mean steps of SUCCESSFUL episodes (goal-reaching time) energy_goal / energy_ratio: successful episodes only
  energy_used        mean energy over all episodes                       battery_left  mean remaining battery over all episodes
  intervention_rate  interventions / decisions (assurance methods)      fallback_rate  fallback decisions / decisions
  safe_stop_rate     fraction of episodes ending in a safe stop          depleted_rate / timeout_rate  likewise
  fallback_success   among episodes in which the fallback acted at least once: fraction that reached the goal
                     (NaN when no episode used the fallback); fallback_episode_rate is the share of such episodes
"""
from __future__ import annotations

import csv
import math
import re
from pathlib import Path

import numpy as np

METRICS = ("success", "collisions", "unsafe", "steps_goal", "energy_used", "battery_left", "energy_ratio", "intervention_rate",
           "fallback_rate", "safe_stop_rate", "depleted_rate", "timeout_rate", "fallback_success", "fallback_episode_rate")
LOWER_IS_BETTER = {"collisions", "unsafe", "steps_goal", "energy_used", "energy_ratio", "safe_stop_rate", "depleted_rate", "timeout_rate"}
_TAG = re.compile(r"^(?P<name>.+?)(?:_s(?P<seed>\d+))?$")
NAN = float("nan")


def _f(x) -> float:
    try:
        return float(x)
    except (TypeError, ValueError):
        return NAN


def _mean(v) -> float:
    v = [x for x in v if not math.isnan(x)]
    return float(np.mean(v)) if v else NAN


def episode_metrics(rows: list[dict]) -> dict:
    n = len(rows)
    if n == 0:
        return {m: NAN for m in METRICS} | {"n_episodes": 0}
    ok = [r for r in rows if r["reason"] == "goal"]
    dec = sum(_f(r.get("decisions", 0)) for r in rows)
    fb_eps = [r for r in rows if _f(r.get("fallback_steps", 0)) > 0]
    return {
        "n_episodes": n,
        "success": len(ok) / n,
        "collisions": _mean([_f(r["collisions"]) for r in rows]),
        "unsafe": _mean([_f(r["attempted_unsafe"]) for r in rows]),
        "steps_goal": _mean([_f(r["steps"]) for r in ok]),
        "energy_used": _mean([_f(r["energy_used"]) for r in rows]),
        "battery_left": _mean([_f(r["battery_left"]) for r in rows]),
        "energy_ratio": _mean([_f(r["energy_ratio"]) for r in ok]),
        "intervention_rate": sum(_f(r.get("interventions", 0)) for r in rows) / dec if dec else NAN,
        "fallback_rate": sum(_f(r.get("fallback_steps", 0)) for r in rows) / dec if dec else NAN,
        "safe_stop_rate": sum(r["reason"] == "safe_stop" for r in rows) / n,
        "depleted_rate": sum(r["reason"] == "battery_depleted" for r in rows) / n,
        "timeout_rate": sum(r["reason"] == "timeout" for r in rows) / n,
        "fallback_success": (sum(r["reason"] == "goal" for r in fb_eps) / len(fb_eps)) if fb_eps else NAN,
        "fallback_episode_rate": len(fb_eps) / n,
    }


def label_of(name: str) -> str:
    """CSV tag name -> method spec label: assured_p95 -> assured@95 ; assured-no_ood_p90 -> assured-no_ood@90."""
    m = re.match(r"^(assured(?:-[a-z_]+)?)_p(\d+)$", name)
    return f"{m.group(1)}@{m.group(2)}" if m else name


def load_run(run_dir, split: str) -> dict:
    """{preset: {method_label: {seed (or None for seedless): [rows]}}} from <run_dir>/<split>/<preset>/<tag>.csv"""
    out: dict = {}
    for pdir in sorted((Path(run_dir) / split).glob("*")):
        if not pdir.is_dir():
            continue
        for f in sorted(pdir.glob("*.csv")):
            m = _TAG.match(f.stem)
            name, seed = m["name"], (int(m["seed"]) if m["seed"] is not None else None)
            with open(f) as fh:
                rows = list(csv.DictReader(fh))
            out.setdefault(pdir.name, {}).setdefault(label_of(name), {})[seed] = rows
    return out


def metrics_table(run: dict) -> dict:
    """{preset: {method: {seed|None: metrics}}}"""
    return {p: {m: {s: episode_metrics(rows) for s, rows in by_seed.items()} for m, by_seed in methods.items()} for p, methods in run.items()}


def per_seed_values(table_pm: dict, metric: str) -> dict:
    """{seed: value} for one (preset, method) block; seedless methods return {None: value}."""
    return {s: m[metric] for s, m in table_pm.items()}
