"""Aggregation + paired comparisons driven by protocol/analysis_plan.json (evaluation side)."""
from __future__ import annotations

import csv
import json
import math
from pathlib import Path

import numpy as np

from src.evaluation.metrics import METRICS, load_run, metrics_table
from src.evaluation.stats import holm, mean_ci, paired_diff, wilson

NAN = float("nan")
PER_EPISODE = {  # metrics that can be recomputed per episode (for seedless methods' interval over maps)
    "collisions": lambda r: float(r["collisions"]), "unsafe": lambda r: float(r["attempted_unsafe"]),
    "energy_used": lambda r: float(r["energy_used"]), "battery_left": lambda r: float(r["battery_left"]),
    "safe_stop_rate": lambda r: float(r["reason"] == "safe_stop"), "depleted_rate": lambda r: float(r["reason"] == "battery_depleted"),
    "timeout_rate": lambda r: float(r["reason"] == "timeout")}


def load_plan(root: Path) -> dict:
    return json.loads((Path(root) / "protocol" / "analysis_plan.json").read_text())


def summarise(run: dict, table: dict, preset: str, method: str, metric: str) -> dict:
    """Mean and 95% interval for one (condition, method, metric): over seeds, or over maps for seedless methods."""
    blk = table[preset][method]
    seeds = sorted(s for s in blk if s is not None)
    if seeds:
        return {**mean_ci([blk[s][metric] for s in seeds]), "basis": "seeds"}
    rows = run[preset][method][None]
    if metric == "success":
        k = sum(r["reason"] == "goal" for r in rows); lo, hi = wilson(k, len(rows))
        return {"n": len(rows), "mean": k / len(rows), "sd": NAN, "lo": lo, "hi": hi, "basis": "maps (Wilson)"}
    if metric in PER_EPISODE:
        c = mean_ci([PER_EPISODE[metric](r) for r in rows]); c["basis"] = "maps"; return c
    v = blk[None][metric]
    return {"n": len(rows), "mean": v, "sd": NAN, "lo": NAN, "hi": NAN, "basis": "maps (no interval)"}


def fmt(c: dict, digits: int = 3) -> str:
    if c["n"] == 0 or math.isnan(c["mean"]):
        return "—"
    if math.isnan(c.get("lo", NAN)):
        return f"{c['mean']:.{digits}f}"
    return f"{c['mean']:.{digits}f} ± {(c['hi'] - c['lo']) / 2:.{digits}f}"


def paired(table: dict, preset: str, a: str, b: str, metric: str) -> dict:
    A, B = table[preset].get(a), table[preset].get(b)
    if A is None or B is None:
        return {"n": 0, "mean_diff": NAN, "lo": NAN, "hi": NAN, "p_t": NAN, "p_perm": NAN}
    sa = sorted(s for s in A if s is not None)
    if not sa:
        raise ValueError(f"{a} has no seeds; the proposed method must be a seeded method")
    if None in B:       # seedless comparator: paired with every seed of A on identical maps
        xs, ys = [A[s][metric] for s in sa], [B[None][metric]] * len(sa)
    else:
        common = [s for s in sa if s in B]
        xs, ys = [A[s][metric] for s in common], [B[s][metric] for s in common]
    return paired_diff(xs, ys)


def paired_family(table: dict, plan: dict, family: str) -> list[dict]:
    """Holm step-down within each (metric, comparison) across the conditions: the claim 'A beats B on metric M' is tested in every
    condition, so the family is the conditions. (A single family over all comparisons cannot reject at n=10 seeds: the exact
    sign-flip p-value has a floor of 2/2^n = 0.00195, above alpha/30.)"""
    rows = []
    for metric in plan["primary_metrics"]:
        for comp in plan[f"{family}_comparisons"]:
            fam = []
            for preset in plan["conditions"]:
                if preset in table:
                    r = paired(table, preset, comp["a"], comp["b"], metric)
                    fam.append({"family": family, "metric": metric, "condition": preset, "comparison": comp["name"], "a": comp["a"], "b": comp["b"], **r})
            for r, adj in zip(fam, holm([x["p_perm"] for x in fam])):
                r["p_holm"] = adj
            rows += fam
    return rows


def write_tables(run_dir: Path, split: str, plan: dict, out_dir: Path) -> dict:
    run = load_run(run_dir, split)
    if not run:
        raise SystemExit(f"no episode files under {run_dir}/{split}")
    table = metrics_table(run)
    out_dir.mkdir(parents=True, exist_ok=True)
    # long-format metrics per seed
    with open(out_dir / "metrics_by_seed.csv", "w", newline="") as f:
        w = csv.writer(f); w.writerow(["condition", "method", "seed", "n_episodes", *METRICS])
        for p, ms in table.items():
            for m, seeds in ms.items():
                for s, v in seeds.items():
                    w.writerow([p, m, "" if s is None else s, v["n_episodes"], *[f"{v[k]:.6g}" for k in METRICS]])

    def md_table(methods, cols, title, digits=3):
        lines = []
        for p in plan["conditions"]:
            if p not in table:
                continue
            ns = sorted({len([s for s in table[p][m] if s is not None]) or 1 for m in methods if m in table[p]})
            nm = {len(next(iter(run[p][m].values()))) for m in methods if m in run[p]}
            lines += [f"\n### {title} — {p}  (seeds per method: {ns}; maps per episode set: {sorted(nm)})\n",
                      "| Method | " + " | ".join(cols) + " |", "|---|" + "---|" * len(cols)]
            for m in methods:
                if m in table[p]:
                    lines.append(f"| {m} | " + " | ".join(fmt(summarise(run, table, p, m, c), digits) for c in cols) + " |")
        return "\n".join(lines) + "\n"
    cols = ["success", "collisions", "unsafe", "steps_goal", "energy_used", "battery_left", "intervention_rate", "safe_stop_rate"]
    (out_dir / "table_main.md").write_text("Mean ± 95% interval (over seeds; over maps for seedless methods).\n" + md_table(plan["main_table_methods"], cols, "Main comparison"))
    (out_dir / "table_ablation.md").write_text(md_table(plan["ablation_methods"], ["success", "collisions", "unsafe", "safe_stop_rate", "intervention_rate", "fallback_rate", "fallback_success"], "Ablation"))
    (out_dir / "table_sensitivity.md").write_text(md_table(plan["sensitivity_methods"], ["success", "collisions", "unsafe", "safe_stop_rate", "intervention_rate"], "Percentile sensitivity"))
    (out_dir / "table_failure_modes.md").write_text(md_table(plan["main_table_methods"], ["success", "safe_stop_rate", "depleted_rate", "timeout_rate"], "Terminal outcomes"))
    paired_rows = paired_family(table, plan, "primary") + paired_family(table, plan, "secondary")
    with open(out_dir / "paired.csv", "w", newline="") as f:
        keys = ["family", "metric", "condition", "comparison", "a", "b", "n", "mean_diff", "lo", "hi", "p_t", "p_perm", "p_holm"]
        w = csv.DictWriter(f, keys); w.writeheader(); w.writerows({k: r.get(k) for k in keys} for r in paired_rows)
    lines = ["Paired differences (A − B) over system seeds on identical maps; 95% t interval; exact sign-flip p; Holm-adjusted across the conditions within each (comparison, metric).\n"
             "For success higher is better; for collisions/unsafe lower is better.\n"]
    for fam in ("primary", "secondary"):
        for metric in plan["primary_metrics"]:
            lines += [f"\n### {fam} comparisons — {metric}\n", "| Condition | Comparison | n | A − B | 95% CI | p (perm) | p (Holm) |", "|---|---|---|---|---|---|---|"]
            for r in paired_rows:
                if r["family"] == fam and r["metric"] == metric and r["n"]:
                    sig = " *" if r["p_holm"] < plan["alpha"] else ""
                    lines.append(f"| {r['condition']} | {r['comparison']} | {r['n']} | {r['mean_diff']:+.4f} | [{r['lo']:+.4f}, {r['hi']:+.4f}] | {r['p_perm']:.4f} | {r['p_holm']:.4f}{sig} |" if r["n"] >= 2 else f"| {r['condition']} | {r['comparison']} | {r['n']} | {r['mean_diff']:+.4f} | n/a (need >= 2 seeds) | n/a | n/a |")
    (out_dir / "table_paired.md").write_text("\n".join(lines) + "\n")
    return {"conditions": list(table), "n_methods": {p: len(table[p]) for p in table}, "paired_rows": len(paired_rows)}
