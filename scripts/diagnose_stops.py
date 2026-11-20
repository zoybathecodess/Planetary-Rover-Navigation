"""Why does the assured controller stop? Joins decision logs with the plain-ensemble outcome on the same map/seed.
  python3 scripts/run_task4.py eval --split val --presets combined_shift --pcts 95 --log-maps 100 --jobs 4
  python3 scripts/diagnose_stops.py --preset combined_shift --pct 95"""
from _common import ROOT  # noqa: F401

import argparse
import collections
import csv
import glob
import json
import re
import statistics as st


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="results/task4"); ap.add_argument("--split", default="val")
    ap.add_argument("--preset", default="combined_shift"); ap.add_argument("--pct", default="95")
    a = ap.parse_args()
    d = (ROOT / a.out) / "eval" / a.split / a.preset
    cause = collections.Counter(); ratio = collections.defaultdict(list); left = collections.defaultdict(list)
    first = collections.defaultdict(list)
    for f in sorted(glob.glob(str(d / "logs" / f"assured_p{a.pct}_s*.jsonl"))):
        s = re.search(r"_s(\d+)\.jsonl", f).group(1)
        ens = {r["map"]: r for r in csv.DictReader(open(d / f"ens_s{s}.csv"))}   # map column is "seed(<n>)"
        for line in open(f):
            e = json.loads(line)
            if e["reason"] != "safe_stop":
                continue
            last = e["decisions"][-1]
            en = ens[f"seed({e['map_seed']})"]
            key = (last["stop_cause"], "ens_goal" if en["success"] == "1" else "ens_fail")
            cause[key] += 1
            if last["route_energy_est"] is not None and last["battery"]:
                ratio[key].append(last["route_energy_est"] / last["battery"])
            if en["success"] == "1":
                left[key].append(float(en["battery_left"]))
            first[key].append(len(e["decisions"]))
    if not cause:
        print("no safe stops in logs: run eval with --log-maps 100 first"); return
    print(f"{a.preset} p{a.pct}: stop cause x what the plain ensemble did on the same map/seed")
    for k, v in sorted(cause.items(), key=lambda kv: -kv[1]):
        r = f"route_est/battery median {st.median(ratio[k]):.2f}" if ratio[k] else "route_est n/a"
        b = f"ensemble battery left at goal median {st.median(left[k]):.0f}" if left[k] else ""
        print(f"  {k[0]:17} {k[1]:9} n={v:4}  stop after median {st.median(first[k]):.0f} decisions  {r}  {b}")


if __name__ == "__main__":
    main()
