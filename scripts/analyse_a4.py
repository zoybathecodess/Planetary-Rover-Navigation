"""Amendment A4 analysis (real-terrain tiles under shifted physics), as pre-registered in protocol/amendment_A4_real_shift.json.

  python3 scripts/analyse_a4.py
Writes results/phase2/a4/analysis/real_final/{table_a4.md, a4_paired.csv}.
"""
from _common import ROOT  # noqa: F401

import csv
import json
import math

from src.evaluation.metrics import episode_metrics, load_run
from src.evaluation.stats import holm, mean_ci, paired_diff, wilson

COND = "real_hirise"


CONDS = ("real_sensor", "real_dynamics", "real_combined")


def main():
    plan = json.loads((ROOT / "protocol/amendment_A4_real_shift.json").read_text())
    run = load_run(ROOT / "results/phase2/a4", "real_final")
    a2 = load_run(ROOT / "results/phase2/a2", "real_final")["real_hirise"]

    def blk(src, m):
        return {s: episode_metrics(rows) for s, rows in src[m].items()}

    for c in CONDS:
        ref = [r["map"] for r in next(iter(run[c]["assured@95"].values()))]
        for m in plan["methods"]:
            for s, rows in run[c][m].items():
                assert [r["map"] for r in rows] == ref, (c, m, s)
    n = 450
    cols = ["success", "unsafe", "collisions", "energy_used", "intervention_rate", "safe_stop_rate", "depleted_rate"]

    def cell(b, c):
        vals = [v[c] for v in b.values()]
        if len(vals) == 1:
            v = vals[0]
            if c in ("success", "safe_stop_rate", "depleted_rate") and not math.isnan(v):
                lo, hi = wilson(round(v * n), n)
                return f"{v:.3f} [{lo:.3f}, {hi:.3f}]"
            return "—" if math.isnan(v) else f"{v:.3f}"
        ci = mean_ci(vals)
        return "—" if math.isnan(ci["mean"]) else f"{ci['mean']:.3f} ± {ci['hi'] - ci['mean']:.3f}"

    L = ["# Amendment A4 — real-terrain tiles under shifted physics", "",
         "450 real_final tiles; mean ± 95% t-interval over 10 seeds (Wilson over tiles for seedless methods).", ""]
    for c in ("real_hirise",) + CONDS:
        src = {"real_hirise": a2}.get(c) or run[c]
        L += [f"### {c}{' (A2, ID physics, for reference)' if c == 'real_hirise' else ''}", "",
              "| Method | " + " | ".join(cols) + " |", "|---" * (len(cols) + 1) + "|"]
        for m in plan["methods"]:
            L.append(f"| {m} | " + " | ".join(cell(blk(src, m), k) for k in cols) + " |")
        L.append("")
    rows = []
    for fam in ("primary_comparisons", "secondary_comparisons"):
        for cmp_ in plan[fam]:
            for metric in plan["primary_metrics"] + plan["secondary_metrics"]:
                res = []
                for c in CONDS:
                    A, B = blk(run[c], cmp_["a"]), blk(run[c], cmp_["b"])
                    seeds = sorted(A)
                    bv = [B[s][metric] for s in seeds] if len(B) > 1 else [next(iter(B.values()))[metric]] * len(seeds)
                    res.append((c, paired_diff([A[s][metric] for s in seeds], bv)))
                for (c, r), h in zip(res, holm([r["p_perm"] for _, r in res])):
                    rows.append({"family": fam.split("_")[0], "comparison": cmp_["name"], "metric": metric, "condition": c, "n": r["n"],
                                 "diff": r["mean_diff"], "lo": r["lo"], "hi": r["hi"], "p_perm": r["p_perm"], "p_holm": h})
    out = ROOT / "results/phase2/a4/analysis/real_final"
    out.mkdir(parents=True, exist_ok=True)
    with open(out / "a4_paired.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, list(rows[0])); w.writeheader(); w.writerows(rows)
    L += ["## Paired differences (A − B); Holm across the three conditions per (comparison, metric)", "",
          "| Family | Comparison | Metric | Condition | A − B | 95% CI | p (perm) | p (Holm) |", "|---|---|---|---|---|---|---|---|"]
    for r in rows:
        L.append(f"| {r['family']} | {r['comparison']} | {r['metric']} | {r['condition']} | {r['diff']:+.4f} | [{r['lo']:+.4f}, {r['hi']:+.4f}] | "
                 f"{r['p_perm']:.4f} | {r['p_holm']:.4f}{' *' if r['p_holm'] < 0.05 else ''} |")
    (out / "table_a4.md").write_text("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
