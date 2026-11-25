"""Amendment A1 (H3) analysis, exactly as pre-registered in protocol/amendment_A1_h3.json.

  python3 scripts/analyse_h3.py --main results/phase2/phase2 --h3 results/phase2/h3
Reads the battery-aware methods from the v1.1 campaign and the energy-blind variants from the A1 run (same maps, same seeds),
writes <h3>/analysis/final/{table_h3.md, h3_paired.csv}.
"""
from _common import ROOT  # noqa: F401

import argparse
import csv
import json
import math

from src.evaluation.metrics import _f, episode_metrics, label_of, load_run
from src.evaluation.stats import holm, mean_ci, paired_diff


def efi_rate(rows):
    fb = [r for r in rows if _f(r.get("fallback_steps", 0)) > 0]
    return (sum(r["reason"] != "battery_depleted" for r in fb) / len(fb)) if fb else float("nan")


def metrics(rows):
    m = episode_metrics(rows)
    m["energy_feasible_intervention_rate"] = efi_rate(rows)
    return m


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--main", default="results/phase2/phase2")
    ap.add_argument("--h3", default="results/phase2/h3")
    a = ap.parse_args()
    plan = json.loads((ROOT / "protocol/amendment_A1_h3.json").read_text())
    main_run, h3_run = load_run(ROOT / a.main, "final"), load_run(ROOT / a.h3, "final")
    conds = plan["conditions"]
    metric_list = [plan["primary_metric"]["name"]] + plan["secondary_metrics"]
    methods = sorted({c[k] for c in plan["comparisons"] for k in ("a", "b")})

    def block(preset, method):
        for run in (main_run, h3_run):
            if method in run.get(preset, {}):
                return {s: metrics(rows) for s, rows in run[preset][method].items()}
        raise SystemExit(f"missing {method} in {preset}")

    # pairing check: identical maps for both sides of every comparison
    for p in conds:
        for c in plan["comparisons"]:
            for side in ("a", "b"):
                src = main_run if c[side] in main_run[p] else h3_run
                assert all(len(v) == 500 for v in src[p][c[side]].values()), (p, c[side])
            ma = [r["map"] for r in (main_run if c["a"] in main_run[p] else h3_run)[p][c["a"]][0]]
            mb = [r["map"] for r in (main_run if c["b"] in main_run[p] else h3_run)[p][c["b"]][0]]
            assert ma == mb, f"maps differ for {c['name']} in {p}"

    out = ROOT / a.h3 / "analysis" / "final"
    out.mkdir(parents=True, exist_ok=True)
    lines = ["# Amendment A1 — H3: battery-aware vs energy-blind fallback", "",
             "Mean ± 95% t-interval over 10 system seeds; 500 identical final-split maps per condition.",
             "EFI = energy-feasible intervention rate: among episodes where the fallback acted, share not ending in battery depletion.", ""]
    cols = ["energy_feasible_intervention_rate", "fallback_success", "depleted_rate", "success", "safe_stop_rate", "energy_used", "collisions", "unsafe"]
    short = {"energy_feasible_intervention_rate": "EFI", "fallback_success": "fallback success", "depleted_rate": "depleted",
             "safe_stop_rate": "safe stop", "energy_used": "energy used"}
    for p in conds:
        lines += [f"### {p}", "", "| Method | " + " | ".join(short.get(c, c) for c in cols) + " |", "|---" * (len(cols) + 1) + "|"]
        for m in methods:
            b = block(p, m)
            cells = []
            for c in cols:
                ci = mean_ci([v[c] for v in b.values()])
                cells.append(f"{ci['mean']:.3f} ± {(ci['hi'] - ci['mean']):.3f}" if not math.isnan(ci["mean"]) else "—")
            lines.append(f"| {m} | " + " | ".join(cells) + " |")
        lines.append("")
    rows = []
    for c in plan["comparisons"]:
        for metric in metric_list:
            res = []
            for p in conds:
                A, B = block(p, c["a"]), block(p, c["b"])
                seeds = sorted(A)
                res.append((p, paired_diff([A[s][metric] for s in seeds], [B[s][metric] for s in seeds])))
            adj = holm([r["p_perm"] for _, r in res])
            for (p, r), h in zip(res, adj):
                rows.append({"comparison": c["name"], "metric": metric, "condition": p, "n": r["n"], "diff": r["mean_diff"],
                             "lo": r["lo"], "hi": r["hi"], "p_perm": r["p_perm"], "p_holm": h,
                             "primary": metric == plan["primary_metric"]["name"]})
    with open(out / "h3_paired.csv", "w", newline="") as f:
        w = csv.DictWriter(f, list(rows[0]))
        w.writeheader(); w.writerows(rows)
    lines += ["## Paired differences (A − B), Holm across the five conditions per (comparison, metric)", ""]
    for c in plan["comparisons"]:
        for metric in metric_list:
            lines += [f"### {c['name']} — {metric}{'  (PRIMARY)' if metric == plan['primary_metric']['name'] else ''}", "",
                      "| Condition | n | A − B | 95% CI | p (perm) | p (Holm) |", "|---|---|---|---|---|---|"]
            for r in rows:
                if r["comparison"] == c["name"] and r["metric"] == metric:
                    star = " *" if r["p_holm"] < 0.05 else ""
                    lines.append(f"| {r['condition']} | {r['n']} | {r['diff']:+.4f} | [{r['lo']:+.4f}, {r['hi']:+.4f}] | "
                                 f"{r['p_perm']:.4f} | {r['p_holm']:.4f}{star} |")
            lines.append("")
    prim = [r for r in rows if r["primary"] and r["comparison"] == plan["comparisons"][0]["name"]]
    pos = [r["condition"] for r in prim if r["diff"] > 0 and r["p_holm"] < 0.05]
    neg = [r["condition"] for r in prim if r["diff"] < 0 and r["p_holm"] < 0.05]
    verdict = ("SUPPORTED" if pos and not neg else "NOT SUPPORTED" if not pos and not neg else "MIXED")
    lines += ["## Pre-registered decision", "", f"Primary comparison: {plan['comparisons'][0]['name']}, metric EFI.",
              f"Significant improvement in: {pos or 'none'}; significant deterioration in: {neg or 'none'}.", f"**H3: {verdict}**", ""]
    (out / "table_h3.md").write_text("\n".join(lines))
    print("\n".join(lines))


if __name__ == "__main__":
    main()
