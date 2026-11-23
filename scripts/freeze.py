"""Freeze / verify the implementation and protocol (Task 5).

  python3 scripts/freeze.py report            run the test suite, write docs/TEST_REPORT.md (JUnit-based)
  python3 scripts/freeze.py freeze            write protocol/freeze.json (refuses on a dirty git tree unless --allow-dirty)
  python3 scripts/freeze.py verify            compare the working tree + artefacts with protocol/freeze.json
"""
from _common import ROOT  # noqa: F401

import argparse
import json
import subprocess
import sys
import time
import xml.etree.ElementTree as ET
from collections import defaultdict

from src.evaluation.reproducibility import FREEZE_PATH, freeze_manifest, git_state, verify_freeze


def cmd_report(a):
    xml = ROOT / "results" / "junit.xml"
    xml.parent.mkdir(parents=True, exist_ok=True)
    r = subprocess.run([sys.executable, "-m", "pytest", "-q", f"--junitxml={xml}", "tests"], cwd=ROOT)
    root = ET.parse(xml).getroot()
    suite = root if root.tag == "testsuite" else root.find("testsuite")
    per = defaultdict(lambda: [0, 0, 0, 0.0])
    fails = []
    for tc in suite.iter("testcase"):
        f = tc.get("classname", "").split(".")[1] if "." in tc.get("classname", "") else tc.get("classname", "?")
        row = per[f]; row[0] += 1; row[3] += float(tc.get("time", 0))
        if tc.find("failure") is not None or tc.find("error") is not None:
            row[1] += 1; fails.append(f"{tc.get('classname')}.{tc.get('name')}")
        elif tc.find("skipped") is not None:
            row[2] += 1
    g = git_state(ROOT)
    lines = ["# Test report", "", f"Generated {time.strftime('%Y-%m-%d %H:%M:%S %z')}  |  commit `{g['commit']}` (dirty: {g['dirty']})", "",
             "| Test file | Tests | Failed | Skipped | Seconds |", "|---|---|---|---|---|"]
    for f, (n, bad, sk, t) in sorted(per.items()):
        lines.append(f"| {f} | {n} | {bad} | {sk} | {t:.1f} |")
    tot = [sum(v[i] for v in per.values()) for i in range(4)]
    lines += [f"| **total** | **{tot[0]}** | **{tot[1]}** | **{tot[2]}** | {tot[3]:.1f} |", ""]
    lines += ["All critical tests pass." if not fails else "FAILURES:\n" + "\n".join(f"- {x}" for x in fails)]
    (ROOT / "docs" / "TEST_REPORT.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    sys.exit(r.returncode)


def cmd_freeze(a):
    g = git_state(ROOT)
    if g["dirty"] and not a.allow_dirty:
        raise SystemExit("git tree has uncommitted changes: commit first (or --allow-dirty for a dry run). A freeze must name a real commit.")
    proto = json.loads((ROOT / "protocol" / "phase2_protocol.json").read_text())
    m = freeze_manifest(ROOT, proto)
    (ROOT / FREEZE_PATH).write_text(json.dumps(m, indent=2))
    print(f"froze commit {m['git']['commit']}  code files {len(m['code'])}  artefacts {len(m['artefacts'])}  threshold sets {len(m['thresholds'])}")
    print(f"-> {FREEZE_PATH}   now commit it and tag the commit, e.g.  git tag v5.0-freeze")


def cmd_verify(a):
    problems = verify_freeze(ROOT)
    print("freeze verification:", "CLEAN" if not problems else f"{len(problems)} difference(s)")
    for p in problems[:50]:
        print("  ", p)
    sys.exit(1 if problems else 0)


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("report")
    f = sub.add_parser("freeze"); f.add_argument("--allow-dirty", action="store_true")
    sub.add_parser("verify")
    a = ap.parse_args()
    {"report": cmd_report, "freeze": cmd_freeze, "verify": cmd_verify}[a.cmd](a)


if __name__ == "__main__":
    main()
