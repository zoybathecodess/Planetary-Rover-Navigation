"""Metrics and statistical comparisons (Task 8 machinery, fixed by protocol/analysis_plan.json).

  python3 scripts/analyse.py --run results/phase2/phase2 --split final
Writes <run>/analysis/<split>/{metrics_by_seed.csv, table_main.md, table_ablation.md, table_sensitivity.md,
table_failure_modes.md, table_paired.md, paired.csv}.   Works on any split directory (use `val` for a dress rehearsal).
"""
from _common import ROOT  # noqa: F401

import argparse
import json
from pathlib import Path

from src.evaluation.analysis import load_plan, write_tables


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", required=True)
    ap.add_argument("--split", default="final")
    a = ap.parse_args()
    run = ROOT / a.run
    info = write_tables(run, a.split, load_plan(ROOT), run / "analysis" / a.split)
    print(json.dumps(info))
    print("tables ->", run / "analysis" / a.split)
    print((run / "analysis" / a.split / "table_main.md").read_text()[:3000])


if __name__ == "__main__":
    main()
