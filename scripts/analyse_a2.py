"""Amendment A2 analysis (real-terrain transfer), exactly as pre-registered in protocol/amendment_A2_real_terrain.json.

  python3 scripts/analyse_a2.py --main results/phase2/phase2 --a2 results/phase2/a2
Writes <a2>/analysis/real_final/{table_a2.md, a2_paired.csv}.
"""
from _common import ROOT  # noqa: F401

import argparse
import csv
import json
import math

from src.evaluation.metrics import episode_metrics, load_run
from src.evaluation.stats import holm, mean_ci, paired_diff, wilson

COND = "real_hirise"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--main", default="results/phase2/phase2")
    ap.add_argument("--a2", default="results/phase2/a2")
    a = ap.parse_args()
    plan = json.loads((ROOT / "protocol/amendment_A2_real_terrain.json").read_text())
    real = load_run(ROOT / a.a2, "real_final")[COND]
    main_id = load_run(ROOT / a.main, "final")["id"]
    a3 = load_run(ROOT / "results/phase2/a3", "final").get("id", {})

    def blk(src, m):
        return {s: episode_metrics(rows) for s, rows in src[m].items()}

    ref = [r["map"] for r in next(iter(real["assured@95"].values()))]
    for m in plan["methods"]:
        for s, rows in real[m].items():
            assert [r["map"] for r in rows] == ref, (m, s)
    n = len(ref)
    cols = ["success", "unsafe", "collisions", "energy_used", "intervention_rate", "safe_stop_rate", "depleted_rate"]

    def cell(b, c):
        vals = [v[c] for v in b.values()]
        if len(vals) == 1:                      # seedless: Wilson for proportions
            v = vals[0]
            if c in ("success", "safe_stop_rate", "depleted_rate") and not math.isnan(v):
                lo, hi = wilson(round(v * n), n)
                return f"{v:.3f} [{lo:.3f}, {hi:.3f}]"
            return "—" if math.isnan(v) else f"{v:.3f}"
        ci = mean_ci(vals)
        return "—" if math.isnan(ci["mean"]) else f"{ci['mean']:.3f} ± {ci['hi'] - ci['mean']:.3f}"

    L = ["# Amendment A2 — real-terrain transfer (HiRISE tiles, ID physics)", "",
         f"{n} real_final tiles; mean ± 95% t-interval over 10 seeds (Wilson over tiles for seedless methods).", "",
         "| Method | " + " | ".join(cols) + " |", "|---" * (len(cols) + 1) + "|"]
    for m in plan["methods"]:
        L.append(f"| {m} | " + " | ".join(cell(blk(real, m), c) for c in cols) + " |")
    L += ["", "## Transfer: procedural ID → real terrain (success / unsafe)", "", "| Method | ID success | real success | ID unsafe | real unsafe |",
          "|---|---|---|---|---|"]
    for m in plan["methods"]:
        src = main_id if m in main_id else a3 if m in a3 else None
        if src is None:
            continue
        bi, br = blk(src, m), blk(real, m)
        f = lambda b, c: sum(v[c] for v in b.values()) / len(b)  # noqa: E731
        L.append(f"| {m} | {f(bi, 'success'):.3f} | {f(br, 'success'):.3f} | {f(bi, 'unsafe'):.3f} | {f(br, 'unsafe'):.3f} |")
    rows = []
    for fam in ("primary_comparisons", "secondary_comparisons"):
        for metric in plan["primary_metrics"] + plan["secondary_metrics"]:
            res = []
            for c in plan[fam]:
                A, B = blk(real, c["a"]), blk(real, c["b"])
                seeds = sorted(A)
                bv = [B[s][metric] for s in seeds] if len(B) > 1 else [next(iter(B.values()))[metric]] * len(seeds)
                res.append((c, paired_diff([A[s][metric] for s in seeds], bv)))
            for (c, r), h in zip(res, holm([r["p_perm"] for _, r in res])):
                rows.append({"family": fam.split("_")[0], "comparison": c["name"], "metric": metric, "n": r["n"], "diff": r["mean_diff"],
                             "lo": r["lo"], "hi": r["hi"], "p_perm": r["p_perm"], "p_holm": h})
    out = ROOT / a.a2 / "analysis" / "real_final"
    out.mkdir(parents=True, exist_ok=True)
    with open(out / "a2_paired.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, list(rows[0])); w.writeheader(); w.writerows(rows)
    L += ["", "## Paired differences (A − B); Holm across the comparisons of a family, per metric", "",
          "| Family | Comparison | Metric | A − B | 95% CI | p (perm) | p (Holm) |", "|---|---|---|---|---|---|---|"]
    for r in rows:
        L.append(f"| {r['family']} | {r['comparison']} | {r['metric']} | {r['diff']:+.4f} | [{r['lo']:+.4f}, {r['hi']:+.4f}] | "
                 f"{r['p_perm']:.4f} | {r['p_holm']:.4f}{' *' if r['p_holm'] < 0.05 else ''} |")
    (out / "table_a2.md").write_text("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
