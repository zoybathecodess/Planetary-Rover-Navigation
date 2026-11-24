"""Amendment A3 analysis (action-conditioned OOD gate), exactly as pre-registered in protocol/amendment_A3_action_ood.json.

  python3 scripts/analyse_a3.py --main results/phase2/phase2 --a3 results/phase2/a3
Writes <a3>/analysis/final/{table_a3.md, a3_paired.csv}.
"""
from _common import ROOT  # noqa: F401

import argparse
import csv
import json
import math

from src.evaluation.metrics import episode_metrics, load_run
from src.evaluation.stats import holm, mean_ci, paired_diff


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--main", default="results/phase2/phase2")
    ap.add_argument("--a3", default="results/phase2/a3")
    a = ap.parse_args()
    plan = json.loads((ROOT / "protocol/amendment_A3_action_ood.json").read_text())
    runs = [load_run(ROOT / a.main, "final"), load_run(ROOT / a.a3, "final")]
    conds = plan["conditions"]

    def rows_of(p, m):
        for r in runs:
            if m in r.get(p, {}):
                return r[p][m]
        raise SystemExit(f"missing {m} in {p}")

    def block(p, m):
        return {s: episode_metrics(rows) for s, rows in rows_of(p, m).items()}

    shown = ["assured@95", "assured-no_ood@95", "assured-aood@95", "assured-ood_only@95", "assured-aood_only@95"]
    for p in conds:   # identical maps for everything compared
        ref = [r["map"] for r in rows_of(p, "assured@95")[0]]
        for m in shown:
            for s, rows in rows_of(p, m).items():
                assert [r["map"] for r in rows] == ref and len(rows) == 500, (p, m, s)

    cols = ["success", "unsafe", "collisions", "intervention_rate", "safe_stop_rate", "energy_used"]
    out = ROOT / a.a3 / "analysis" / "final"
    out.mkdir(parents=True, exist_ok=True)
    L = ["# Amendment A3 — action-conditioned OOD gate", "",
         "Mean ± 95% t-interval over 10 system seeds; 500 identical final-split maps per condition.", ""]
    for p in conds:
        L += [f"### {p}", "", "| Method | " + " | ".join(cols) + " |", "|---" * (len(cols) + 1) + "|"]
        for m in shown:
            b = block(p, m)
            cells = []
            for c in cols:
                ci = mean_ci([v[c] for v in b.values()])
                cells.append("—" if math.isnan(ci["mean"]) else f"{ci['mean']:.3f} ± {ci['hi'] - ci['mean']:.3f}")
            L.append(f"| {m} | " + " | ".join(cells) + " |")
        L.append("")
    rows = []
    for c in plan["comparisons"]:
        for metric in plan["primary_metrics"] + plan["secondary_metrics"]:
            res = []
            for p in conds:
                A, B = block(p, c["a"]), block(p, c["b"])
                res.append((p, paired_diff([A[s][metric] for s in sorted(A)], [B[s][metric] for s in sorted(A)])))
            for (p, r), h in zip(res, holm([r["p_perm"] for _, r in res])):
                rows.append({"comparison": c["name"], "metric": metric, "condition": p, "n": r["n"], "diff": r["mean_diff"],
                             "lo": r["lo"], "hi": r["hi"], "p_perm": r["p_perm"], "p_holm": h,
                             "primary": metric in plan["primary_metrics"]})
    with open(out / "a3_paired.csv", "w", newline="") as f:
        w = csv.DictWriter(f, list(rows[0])); w.writeheader(); w.writerows(rows)
    L += ["## Paired differences (A − B); Holm across conditions per (comparison, metric)", ""]
    for c in plan["comparisons"]:
        for metric in plan["primary_metrics"] + plan["secondary_metrics"]:
            L += [f"### {c['name']} — {metric}{'  (PRIMARY)' if metric in plan['primary_metrics'] else ''}", "",
                  "| Condition | n | A − B | 95% CI | p (perm) | p (Holm) |", "|---|---|---|---|---|---|"]
            for r in rows:
                if r["comparison"] == c["name"] and r["metric"] == metric:
                    L.append(f"| {r['condition']} | {r['n']} | {r['diff']:+.4f} | [{r['lo']:+.4f}, {r['hi']:+.4f}] | {r['p_perm']:.4f} | "
                             f"{r['p_holm']:.4f}{' *' if r['p_holm'] < 0.05 else ''} |")
            L.append("")

    def better(r):   # success higher / unsafe lower is better
        return r["p_holm"] < 0.05 and ((r["metric"] == "success" and r["diff"] > 0) or (r["metric"] == "unsafe" and r["diff"] < 0))

    def worse(r):
        return r["p_holm"] < 0.05 and ((r["metric"] == "success" and r["diff"] < 0) or (r["metric"] == "unsafe" and r["diff"] > 0))

    prim = lambda name: [r for r in rows if r["primary"] and r["comparison"] == name]  # noqa: E731
    c1, c2 = (prim(c["name"]) for c in plan["comparisons"])
    gain1 = [f"{r['condition']}/{r['metric']}" for r in c1 if better(r) and r["condition"] in ("sensor_shift", "combined_shift")]
    loss1 = [f"{r['condition']}/{r['metric']}" for r in c1 if worse(r)]
    gain2 = [f"{r['condition']}/{r['metric']}" for r in c2 if better(r)]
    loss2 = [f"{r['condition']}/{r['metric']}" for r in c2 if worse(r)]
    v1 = "SUPPORTED" if gain1 and not loss1 else ("MIXED" if gain1 else "NOT SUPPORTED")
    v2 = "ADDS VALUE" if gain2 and not loss2 else ("MIXED" if gain2 else "NO ADDED VALUE")
    L += ["## Pre-registered decisions", "",
          f"Comparison 1 (action-OOD vs raw-OOD): improvements under sensor/combined: {gain1 or 'none'}; deteriorations anywhere: {loss1 or 'none'}.",
          f"**H2': {v1}**", "",
          f"Comparison 2 (action-OOD vs no OOD): improvements: {gain2 or 'none'}; deteriorations: {loss2 or 'none'}.",
          f"**Action-conditioned OOD gate: {v2}**", ""]
    (out / "table_a3.md").write_text("\n".join(L))
    print("\n".join(L))


if __name__ == "__main__":
    main()
