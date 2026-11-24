"""Task 6: statistics, metrics, paired analysis, analysis-plan consistency, shift documentation."""
import csv
import importlib.util
import json
import math
import tempfile
import unittest
from pathlib import Path

import numpy as np

from src.evaluation import analysis as A
from src.evaluation import stats as S
from src.evaluation.experiment import parse_method
from src.evaluation.harness import ROW_FIELDS
from src.evaluation.metrics import METRICS, episode_metrics, label_of, load_run, metrics_table
from src.evaluation.reproducibility import CODE_GLOBS

ROOT = Path(__file__).resolve().parents[1]


def row(reason="goal", steps=80, energy=100, coll=0, unsafe=0, dec=80, interv=0, fb=0, ratio=1.4, left=None, method="m", preset="id", mp="seed(1)"):
    return {"method": method, "preset": preset, "map": mp, "success": int(reason == "goal"), "reason": reason, "steps": steps, "reward": 0,
            "battery_left": 250 - energy if left is None else left, "energy_used": energy, "collisions": coll, "attempted_unsafe": unsafe,
            "interventions": interv, "decisions": dec, "no_safe_action": 0, "fallback_steps": fb, "unc_alarms": 0, "ood_alarms": 0,
            "monitor_rejects": 0, "optimal_cost": 70, "energy_ratio": ratio if reason == "goal" else "nan", "plan_ms": 0}


class TestStats(unittest.TestCase):
    def test_t_critical_values_match_tables(self):
        for df, v in ((1, 12.7062), (4, 2.7764), (9, 2.2622), (29, 2.0452), (99, 1.9842)):
            self.assertAlmostEqual(S.t_crit(df), v, places=3)
        self.assertAlmostEqual(S.t_crit(9, 0.99), 3.2498, places=3)
        self.assertAlmostEqual(S.t_two_sided_p(2.5, 9), 0.033862, places=5)

    def test_mean_ci(self):
        c = S.mean_ci([1, 2, 3, 4, 5])
        self.assertAlmostEqual(c["mean"], 3); self.assertAlmostEqual(c["hi"] - 3, 2.7764 * math.sqrt(2.5) / math.sqrt(5), places=3)
        self.assertTrue(math.isnan(S.mean_ci([1.0])["lo"])); self.assertEqual(S.mean_ci([float("nan"), 2.0, 4.0])["n"], 2)

    def test_wilson(self):
        lo, hi = S.wilson(8, 10)
        self.assertAlmostEqual(lo, 0.4902, places=3); self.assertAlmostEqual(hi, 0.9433, places=3)
        lo, hi = S.wilson(0, 20); self.assertAlmostEqual(lo, 0.0, places=9); self.assertTrue(0 < hi < 0.2)

    def test_sign_flip_exact(self):
        self.assertAlmostEqual(S.sign_flip_p([1, 1, 1, 1]), 2 / 16)
        self.assertAlmostEqual(S.sign_flip_p([1, -1]), 1.0)
        self.assertEqual(S.sign_flip_p([0, 0]), 1.0)
        self.assertAlmostEqual(S.sign_flip_p([1] * 10), 2 / 1024)

    def test_holm_matches_reference(self):
        self.assertEqual([round(x, 10) for x in S.holm([0.01, 0.04, 0.03])], [0.03, 0.06, 0.06])
        adj = S.holm([0.5, float("nan"), 0.001])
        self.assertAlmostEqual(adj[2], 0.002); self.assertTrue(math.isnan(adj[1]))
        self.assertTrue(all(a >= p for a, p in zip(S.holm([0.2, 0.01, 0.03, 0.04]), [0.2, 0.01, 0.03, 0.04])))

    def test_holm_over_five_conditions_can_reject_at_ten_seeds_but_a_single_big_family_cannot(self):
        floor = 2 / 1024                       # smallest exact sign-flip p with 10 seeds
        self.assertAlmostEqual(S.sign_flip_p([1] * 10), floor)
        self.assertLess(S.holm([floor] * 5)[0], 0.05)       # plan v1.1: family = the five conditions
        self.assertGreater(S.holm([floor] * 36)[0], 0.05)   # plan v1.0 (one family of all comparisons): impossible to reject

    def test_paired_diff_uses_pairs_and_ignores_nan(self):
        r = S.paired_diff([1, 2, 3, 4, 5, float("nan")], [1, 1, 2, 2, 3, 9])
        self.assertEqual(r["n"], 5); self.assertAlmostEqual(r["mean_diff"], 1.2)
        self.assertLess(r["lo"], 1.2 < r["hi"])
        r0 = S.paired_diff([1, 1, 1], [1, 1, 1]); self.assertEqual((r0["mean_diff"], r0["p_t"], r0["p_perm"]), (0.0, 1.0, 1.0))


class TestMetrics(unittest.TestCase):
    def test_every_outcome_type_is_counted_correctly(self):
        rows = [row("goal", steps=60, energy=90, coll=1, unsafe=2, interv=5, fb=3, ratio=1.2), row("goal", steps=100, energy=150, ratio=1.6, fb=0),
                row("safe_stop", steps=40, energy=60, fb=4), row("battery_depleted", steps=200, energy=250, coll=5, unsafe=5, left=0),
                row("timeout", steps=300, energy=200)]
        m = episode_metrics(rows)
        self.assertAlmostEqual(m["success"], 0.4); self.assertAlmostEqual(m["safe_stop_rate"], 0.2)
        self.assertAlmostEqual(m["depleted_rate"], 0.2); self.assertAlmostEqual(m["timeout_rate"], 0.2)
        self.assertAlmostEqual(m["collisions"], 1.2); self.assertAlmostEqual(m["unsafe"], 1.4)
        self.assertAlmostEqual(m["steps_goal"], 80); self.assertAlmostEqual(m["energy_ratio"], 1.4)
        self.assertAlmostEqual(m["energy_used"], 150); self.assertAlmostEqual(m["intervention_rate"], 5 / 400)
        self.assertAlmostEqual(m["fallback_rate"], 7 / 400)
        self.assertAlmostEqual(m["fallback_episode_rate"], 0.4); self.assertAlmostEqual(m["fallback_success"], 0.5)   # fallback in {goal, safe_stop}
        self.assertEqual(set(METRICS) - set(m), set())

    def test_no_successes_and_no_fallback_give_nan_not_zero(self):
        m = episode_metrics([row("battery_depleted", left=0), row("timeout")])
        self.assertTrue(math.isnan(m["steps_goal"]) and math.isnan(m["energy_ratio"]) and math.isnan(m["fallback_success"]))
        self.assertEqual(m["success"], 0.0)

    def test_labels_and_loading(self):
        self.assertEqual(label_of("assured_p95"), "assured@95"); self.assertEqual(label_of("assured-no_ood_p90"), "assured-no_ood@90")
        self.assertEqual(label_of("dqn_shield"), "dqn_shield")
        with tempfile.TemporaryDirectory() as t:
            for tag in ("astar", "dqn_shield_s3", "assured-no_stop_p95_s1"):
                d = Path(t) / "final" / "id"; d.mkdir(parents=True, exist_ok=True)
                with open(d / f"{tag}.csv", "w", newline="") as f:
                    w = csv.DictWriter(f, ROW_FIELDS); w.writeheader(); w.writerow(row())
            run = load_run(t, "final")
            self.assertEqual(set(run["id"]), {"astar", "dqn_shield", "assured-no_stop@95"})
            self.assertEqual(set(run["id"]["astar"]), {None}); self.assertEqual(set(run["id"]["dqn_shield"]), {3})


def synthetic_run(t, n_seeds=10, n_maps=20, a_success=1.0, b_success=0.5, shifts=("id", "terrain_shift")):
    """B (dqn_shield) succeeds on a fixed share of maps; A (assured@95) always succeeds with fewer collisions; astar is seedless."""
    for preset in shifts:
        d = Path(t) / "final" / preset; d.mkdir(parents=True, exist_ok=True)
        def write(tag, f_ok, coll):
            with open(d / f"{tag}.csv", "w", newline="") as f:
                w = csv.DictWriter(f, ROW_FIELDS); w.writeheader()
                for i in range(n_maps):
                    ok = (i / n_maps) < f_ok
                    w.writerow(row("goal" if ok else "timeout", coll=coll, unsafe=coll, mp=f"seed({40000 + i})"))
        write("astar", 0.9, 1); write("astar_monitor", 0.85, 1)
        for k in range(n_seeds):
            write(f"assured_p95_s{k}", a_success, 0)
            write(f"dqn_shield_s{k}", b_success, 2)
            for other in ("dqn", "ppo_shield", "ens", "assured-unc_only_p95", "assured-no_stop_p95", "assured-monitor_only_p95", "assured-no_ood_p95",
                          "assured-no_unc_p95", "assured-no_monitor_p95"):
                write(f"{other}_s{k}", 0.8, 1)


class TestAnalysis(unittest.TestCase):
    def test_paired_comparison_recovers_a_known_effect(self):
        with tempfile.TemporaryDirectory() as t:
            synthetic_run(t)
            run = load_run(t, "final"); table = metrics_table(run)
            r = A.paired(table, "id", "assured@95", "dqn_shield", "success")
            self.assertEqual(r["n"], 10); self.assertAlmostEqual(r["mean_diff"], 0.5)
            self.assertAlmostEqual(r["p_perm"], 2 / 1024)
            c = A.paired(table, "id", "assured@95", "dqn_shield", "collisions"); self.assertAlmostEqual(c["mean_diff"], -2.0)
            s = A.paired(table, "id", "assured@95", "astar", "success")          # seedless comparator broadcast over the 10 seeds
            self.assertEqual(s["n"], 10); self.assertAlmostEqual(s["mean_diff"], 1.0 - 0.9)

    def test_summary_intervals_over_seeds_and_over_maps(self):
        with tempfile.TemporaryDirectory() as t:
            synthetic_run(t)
            run = load_run(t, "final"); table = metrics_table(run)
            self.assertEqual(A.summarise(run, table, "id", "dqn_shield", "success")["basis"], "seeds")
            c = A.summarise(run, table, "id", "astar", "success")
            self.assertIn("Wilson", c["basis"]); self.assertAlmostEqual(c["mean"], 0.9); self.assertTrue(c["lo"] < 0.9 < c["hi"])

    def test_write_tables_end_to_end_and_holm_is_applied_per_family(self):
        plan = A.load_plan(ROOT)
        with tempfile.TemporaryDirectory() as t:
            synthetic_run(t)
            out = Path(t) / "out"
            info = A.write_tables(Path(t), "final", plan, out)
            self.assertEqual(info["conditions"], ["id", "terrain_shift"])
            for f in ("metrics_by_seed.csv", "table_main.md", "table_ablation.md", "table_sensitivity.md", "table_failure_modes.md", "table_paired.md", "paired.csv"):
                self.assertTrue((out / f).exists(), f)
            rows = list(csv.DictReader(open(out / "paired.csv")))
            prim = [r for r in rows if r["family"] == "primary" and r["metric"] == "success" and r["n"] != "0"]
            self.assertTrue(prim)
            for r in prim:
                self.assertGreaterEqual(float(r["p_holm"]), float(r["p_perm"]))
            # family = conditions within one (comparison, metric): 2 conditions here, so the adjusted p of an exact floor-p effect is 2x
            dqn = [r for r in prim if r["comparison"] == "assured vs DQN+shield"]
            self.assertEqual(len(dqn), 2); self.assertAlmostEqual(float(dqn[0]["p_holm"]), 2 * 2 / 1024, places=6)
            self.assertTrue(any(float(r["p_holm"]) > float(r["p_perm"]) + 1e-9 for r in prim), "Holm adjustment was not applied")
            self.assertIn("assured@95", (out / "table_main.md").read_text())

    def test_single_seed_is_reported_as_not_estimable_not_as_nan(self):
        plan = A.load_plan(ROOT)
        with tempfile.TemporaryDirectory() as t:
            synthetic_run(t, n_seeds=1)
            A.write_tables(Path(t), "final", plan, Path(t) / "out")
            self.assertIn("need >= 2 seeds", (Path(t) / "out/table_paired.md").read_text())


class TestPlanAndDocs(unittest.TestCase):
    plan = json.loads((ROOT / "protocol/analysis_plan.json").read_text())

    def test_every_method_in_the_plan_is_valid_and_runnable_by_the_default_campaign(self):
        spec = importlib.util.spec_from_file_location("run_experiment", ROOT / "scripts/run_experiment.py")
        src = (ROOT / "scripts/run_experiment.py").read_text()
        default = src.split("DEFAULT_METHODS = (")[1].split(")")[0].replace('"', "").replace("\n", "").replace(" ", "")
        campaign = set(default.split(","))
        named = set(self.plan["main_table_methods"]) | set(self.plan["ablation_methods"]) | set(self.plan["sensitivity_methods"])
        for c in self.plan["primary_comparisons"] + self.plan["secondary_comparisons"]:
            named |= {c["a"], c["b"]}
        for m in named:
            parse_method(m)
            canon = m if "@95" not in m else m.replace("@95", "")
            self.assertIn(canon, campaign, f"{m} is in the plan but not produced by the default campaign")

    def test_plan_metrics_exist_and_primary_set_is_small(self):
        for m in self.plan["primary_metrics"] + self.plan["secondary_metrics"]:
            self.assertIn(m, METRICS)
        self.assertLessEqual(len(self.plan["primary_metrics"]), 3)
        self.assertEqual(self.plan["conditions"], ["id", "terrain_shift", "sensor_shift", "dynamics_shift", "combined_shift"])

    def test_plan_is_covered_by_the_freeze(self):
        self.assertIn("protocol/analysis_plan.json", CODE_GLOBS)
        self.assertIn("protocol/phase2_protocol.json", CODE_GLOBS)

    def test_shift_level_document_is_up_to_date(self):
        spec = importlib.util.spec_from_file_location("describe_presets", ROOT / "scripts/describe_presets.py")
        import sys
        sys.path.insert(0, str(ROOT / "scripts"))
        mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
        self.assertEqual(mod.render(), (ROOT / "docs/SHIFT_LEVELS.md").read_text())

    def test_protocol_json_agrees_with_the_runner_defaults(self):
        proto = json.loads((ROOT / "protocol/phase2_protocol.json").read_text())
        self.assertEqual(proto["evaluation"]["maps_per_preset"], 500)
        self.assertIn("--n-maps", (ROOT / "docs/REPRODUCE.md").read_text())
        self.assertIn('else 500)', (ROOT / "scripts/run_experiment.py").read_text())


if __name__ == "__main__":
    unittest.main()
