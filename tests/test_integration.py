"""Task 5: integration, stress and protocol-hygiene tests (all presets, termination bookkeeping, determinism, pairing,
fuzzing, split disjointness, hidden-state scan, manifests, freeze, held-out-split ledger)."""
import ast
import hashlib
import json
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path

import numpy as np

from src.assurance import layout as L
from src.assurance.controller import RuntimeAssuranceController
from src.assurance.ensemble import EnsemblePolicy
from src.assurance.ood import MahalanobisOOD
from src.config import AssuranceConfig, load_config
from src.evaluation import reproducibility as R
from src.evaluation.evaluator import make_env
from src.evaluation.experiment import PRESETS, check_pairing, method_tag, parse_method, validate_rows
from src.evaluation.harness import evaluate_method
from src.policies.astar_battery import BatteryAwareAStar
from src.policies.baseline_policies import RandomPolicy
from src.policies.rule_shield import RuleShield
from src.policies.sim32_heuristic import ReactiveExplorer
from tests.test_assurance import controller
from tests.test_task3 import fake_obs, flat, known_map

ROOT = Path(__file__).resolve().parents[1]


class GoalHeuristicEnsemble:
    """Hand-made 'members' (no training needed): exercises the full assurance loop on every preset."""
    def q_matrix(self, obs):
        g = np.array([-obs[2], obs[2], -obs[3], obs[3]])
        return np.stack([g + 0.01 * k * np.arange(4) for k in range(3)])
    summarise = staticmethod(EnsemblePolicy.summarise)


def assured(tau_ood=5.0, **kw):
    ood = MahalanobisOOD(); ood.mu = np.zeros(len(L.OOD_FEATURES)); ood.prec = np.eye(len(L.OOD_FEATURES)); ood.score = lambda o: 1.0
    return RuntimeAssuranceController(GoalHeuristicEnsemble(), ood, BatteryAwareAStar(), replace(AssuranceConfig(), **kw), 10.0, tau_ood)


def policies():
    class GoalHeuristicBase:
        name = "base"
        def act(self, obs): return int(np.argmax([-obs[2], obs[2], -obs[3], obs[3]]))
        def q_values(self, obs): return np.array([-obs[2], obs[2], -obs[3], obs[3]])
    return {"astar": BatteryAwareAStar(), "reactive": ReactiveExplorer(0), "random": RandomPolicy(0),
            "shield": RuleShield(GoalHeuristicBase()), "assured": assured()}


class TestSmokeAllPresets(unittest.TestCase):
    def test_every_method_on_every_preset_records_consistent_outcomes(self):
        for preset in PRESETS:
            by = {}
            for name, pol in policies().items():
                rows, summ = evaluate_method(pol, ROOT / f"configs/sim32_{preset}.yaml", range(10000, 10003), name, preset)
                self.assertEqual(validate_rows(rows), [], f"{name}/{preset}")
                by[name] = rows
            self.assertEqual(check_pairing(by), [], preset)

    def test_every_terminal_reason_is_recorded_consistently(self):
        cfg = load_config(ROOT / "configs/sim32_id.yaml")
        seen = {}
        # goal / safe_stop / battery_depleted / timeout, each forced
        class Stop:
            stats = None
            def act(self, obs): return L.STOP_ACTION
        class Dither:
            stats = None
            def __init__(self): self.i = 0
            def act(self, obs): self.i += 1; return 0 if self.i % 2 else 1      # up/down forever, never reaches the goal
        import yaml
        for name, pol, patch in (("goal", BatteryAwareAStar(), {}), ("safe_stop", Stop(), {}), ("battery_depleted", Dither(), {}),
                                 ("timeout", Dither(), {"max_steps": 20})):
            with tempfile.TemporaryDirectory() as t:
                p = Path(t) / "c.yaml"
                d = yaml.safe_load((ROOT / "configs/sim32_id.yaml").read_text()); d["env"].update(patch); p.write_text(yaml.safe_dump(d))
                rows, _ = evaluate_method(pol, p, [10000], name, "id")
            seen[name] = rows[0]["reason"]
            self.assertEqual(validate_rows(rows), [], name)
        self.assertEqual(seen, {"goal": "goal", "safe_stop": "safe_stop", "battery_depleted": "battery_depleted", "timeout": "timeout"})

    def test_validate_rows_flags_inconsistent_records(self):
        env, ev = make_env(load_config(ROOT / "configs/sim32_id.yaml").env, 0)
        rows, _ = evaluate_method(BatteryAwareAStar(), ROOT / "configs/sim32_id.yaml", [10000], "a", "id")
        good = dict(rows[0])
        for key, val in (("success", 0), ("reason", "exploded"), ("battery_left", 5), ("energy_ratio", "nan")):
            self.assertTrue(validate_rows([{**good, key: val}]), key)


class TestDeterminism(unittest.TestCase):
    def test_same_seeds_same_episodes_for_every_method(self):
        def run(pol):
            rows, _ = evaluate_method(pol, ROOT / "configs/sim32_combined_shift.yaml", range(10000, 10003), "m", "combined_shift")
            return [{k: (None if isinstance(v, float) and v != v else v) for k, v in r.items() if k != "plan_ms"} for r in rows]   # NaN != NaN
        for name in ("astar", "shield", "assured", "reactive"):
            self.assertEqual(run(policies()[name]), run(policies()[name]), name)

    def test_paired_methods_see_identical_maps_and_optimal_costs(self):
        a, _ = evaluate_method(BatteryAwareAStar(), ROOT / "configs/sim32_id.yaml", range(10000, 10004), "a", "id")
        b, _ = evaluate_method(ReactiveExplorer(0), ROOT / "configs/sim32_id.yaml", range(10000, 10004), "b", "id")
        self.assertEqual([(r["map"], r["optimal_cost"]) for r in a], [(r["map"], r["optimal_cost"]) for r in b])


class TestAStarMonitorBaseline(unittest.TestCase):
    def build(self):
        from src.evaluation.experiment import build_method
        return build_method("astar_monitor", 0, ROOT)

    def test_spec_and_runs_on_every_preset_with_consistent_records(self):
        self.assertEqual(method_tag("astar_monitor", 7), "astar_monitor")
        for preset in PRESETS:
            rows, _ = evaluate_method(self.build(), ROOT / f"configs/sim32_{preset}.yaml", range(10000, 10003), "astar_monitor", preset)
            self.assertEqual(validate_rows(rows), [], preset)

    def test_identical_to_plain_astar_when_the_monitor_is_quiet(self):
        pol = self.build(); plain = BatteryAwareAStar()
        m = known_map(flat())
        pol.attach(lambda: m, 250); plain.attach(lambda: m, 250)
        o = fake_obs((5, 5), (25, 25), 1.0, window=np.full((5, 5), 0.2)); o[L.IDX_STEPS] = 0.1
        self.assertEqual(pol.act(o), plain.act(o)); self.assertEqual(pol.last_decision["source"], "policy")

    def test_monitor_vetoes_an_astar_move_into_a_believed_obstacle(self):
        pol = self.build()
        g = flat(); m = known_map(g)
        w = np.full((5, 5), 0.2); w[3, 2] = 1.0                 # obstacle directly below the rover
        pol.attach(lambda: m, 250)
        o = fake_obs((5, 5), (25, 5), 1.0, window=w); o[L.IDX_STEPS] = 0.1   # goal straight down: A* wants to go down
        pol.ens.planner.act = lambda obs: 1                      # force the proposal into the obstacle
        a = pol.act(o)
        self.assertNotEqual(a, 1); self.assertIn("obstacle_proximity", pol.last_decision["reasons"])


class TestFuzz(unittest.TestCase):
    def test_controller_never_raises_and_always_returns_a_valid_decision(self):
        rng = np.random.default_rng(0)
        for i in range(400):
            grid = rng.integers(0, 4, size=(32, 32)).astype(np.int64)
            pos = (int(rng.integers(0, 32)), int(rng.integers(0, 32))); goal = (int(rng.integers(0, 32)), int(rng.integers(0, 32)))
            o = fake_obs(pos, goal, float(rng.uniform(0, 1)), window=rng.uniform(0, 1, (5, 5)))
            o[L.IDX_SLIP], o[L.IDX_CONF], o[L.IDX_STEPS] = rng.uniform(0, 1, 3)
            q = rng.normal(size=(3, 4)) * rng.choice([0.01, 1, 100])
            c, _ = controller(q, ood_score=float(rng.choice([0.5, 50.0])), tau_unc=float(rng.choice([0.1, 10.0])), grid=grid, pos=pos, goal=goal,
                              battery=float(rng.uniform(0, 1)), window=o[L.WIN0:L.WIN0 + 25].reshape(5, 5))
            a = c.act(o)
            self.assertIn(a, (0, 1, 2, 3, L.STOP_ACTION), i)
            self.assertEqual(c.last_decision["action"], a)
            if a != L.STOP_ACTION:
                self.assertEqual(c.monitor.check(o, a, c._get_map(), hard_only=True), [] if c.last_decision["source"] == "fallback" else c.monitor.check(o, a, c._get_map(), hard_only=True))

    def test_non_finite_observation_triggers_a_safe_stop(self):
        c, o = controller([[0, 9, 1, 0], [0, 9, 1, 0], [0, 9, 1, 0]])
        for bad in (np.nan, np.inf, -np.inf):
            o2 = o.copy(); o2[10] = bad
            self.assertEqual(c.act(o2), L.STOP_ACTION)
            self.assertEqual(c.last_decision["stop_cause"], "invalid_observation")


class TestSplitHygiene(unittest.TestCase):
    @staticmethod
    def grid_hashes(env, seeds):
        out = {}
        for s in seeds:
            env.reset(seed=s) if s is not None else env.reset()
            out[s if s is not None else len(out)] = hashlib.sha256(env._world.grid.tobytes()).hexdigest()   # evaluator-side check
        return out

    def test_training_stream_and_all_evaluation_splits_share_no_map(self):
        cfg = load_config(ROOT / "configs/sim32_id.yaml")
        env, _ = make_env(cfg.env, 0)
        train = {env.reset() is not None and hashlib.sha256(env._world.grid.tobytes()).hexdigest() for _ in range(150)}
        groups = {name: set(self.grid_hashes(env, range(R.SPLIT_OFFSET[name], R.SPLIT_OFFSET[name] + 60)).values()) for name in R.SPLIT_OFFSET}
        for a in groups:
            self.assertEqual(len(groups[a]), 60, f"{a} has duplicate maps")
            self.assertFalse(groups[a] & train, f"{a} overlaps the training stream")
            for b in groups:
                if a < b:
                    self.assertFalse(groups[a] & groups[b], f"{a} / {b} overlap")

    def test_split_ranges_are_disjoint_for_realistic_sizes(self):
        offs = sorted(R.SPLIT_OFFSET.values())
        self.assertTrue(all(b - a >= 10_000 for a, b in zip(offs, offs[1:])))

    def test_training_does_not_evaluate_on_test_maps_by_default(self):
        from src.config import RunConfig
        self.assertFalse(RunConfig().final_test_eval)


class TestHiddenStateScan(unittest.TestCase):
    PRIVATE = {"_world", "_slip", "_lut", "_ref_lut", "_slip_rng", "_sens_rng", "optimal_cost", "true_slip", "true_energy_table", "commanded_cell_unsafe"}

    def test_policies_agents_and_assurance_never_touch_ground_truth(self):
        for pkg in ("src/policies", "src/agents", "src/assurance"):
            for f in (ROOT / pkg).glob("*.py"):
                tree = ast.parse(f.read_text())
                for node in ast.walk(tree):
                    if isinstance(node, ast.Attribute):
                        self.assertNotIn(node.attr, self.PRIVATE, f"{f.name}: {node.attr}")
                    mods = [a.name for a in node.names] if isinstance(node, ast.Import) else [node.module or ""] if isinstance(node, ast.ImportFrom) else []
                    for m in mods:
                        self.assertFalse(m.startswith("src.evaluation") or m.endswith("procgen"), f"{f.name} imports {m}")

    def test_env_public_api_exposes_no_ground_truth(self):
        env, _ = make_env(load_config(ROOT / "configs/sim32_id.yaml").env, 0)
        env.reset(seed=1)
        pub = [n for n in dir(env) if not n.startswith("_")]
        for n in pub:
            self.assertFalse(isinstance(getattr(env, n), np.ndarray) and getattr(env, n).shape == (32, 32), n)


class TestThresholdHygiene(unittest.TestCase):
    def test_run_task4_calibrates_on_id_validation_only(self):
        src = (ROOT / "scripts/run_task4.py").read_text()
        i, j = src.index("def _calibrate_one"), src.index("def thresholds(")
        body = src[i:j]
        self.assertIn('SPLIT_OFFSET["val"]', body)
        self.assertNotIn("test", body.replace("tests", ""))
        self.assertNotIn("shift", body)
        self.assertIn("CONFIG", body)            # the in-distribution ensemble config, never a shifted preset

    def test_thresholds_depend_only_on_stored_id_scores(self):
        with tempfile.TemporaryDirectory() as t:
            d = Path(t) / "results/task4/calib/ens_s0"; d.mkdir(parents=True)
            np.savez(d / "id_val_scores.npz", unc=np.arange(1000.0), ood=np.arange(1000.0) / 10)
            tab = R.thresholds_table(Path(t))
            v = tab["results/task4/calib/ens_s0"]["p95"]
            self.assertAlmostEqual(v["tau_unc"], np.percentile(np.arange(1000.0), 95)); self.assertAlmostEqual(v["tau_ood"], 94.905, places=2)


class TestManifestFreezeLedger(unittest.TestCase):
    def make_repo(self, t):
        root = Path(t)
        (root / "src").mkdir(); (root / "configs").mkdir(); (root / "scripts").mkdir(); (root / "tests").mkdir()
        (root / "src/a.py").write_text("x = 1\n"); (root / "configs/c.yaml").write_text("a: 1\n")
        ck = root / "results/task3/train/dqn_s0/checkpoints"; ck.mkdir(parents=True); (ck / "best_val.pt").write_bytes(b"weights")
        return root

    def test_manifest_has_the_required_fields(self):
        with tempfile.TemporaryDirectory() as t:
            root = self.make_repo(t)
            m = R.run_manifest(root, kind="x", configs=["configs/c.yaml"], seeds="0-9", artefacts=R.artefact_hashes(root))
            for k in ("argv", "git", "software", "configs", "seeds", "split_offsets", "artefacts", "created"):
                self.assertIn(k, m)
            self.assertIn("python", m["software"]); self.assertIn("numpy", m["software"]); self.assertIn("platform", m["software"])
            self.assertEqual(m["configs"]["configs/c.yaml"]["sha256"], R.sha256_file(root / "configs/c.yaml"))
            self.assertEqual(len(m["artefacts"]), 1)

    def test_verify_detects_code_checkpoint_and_threshold_changes(self):
        with tempfile.TemporaryDirectory() as t:
            root = self.make_repo(t)
            (root / "protocol").mkdir()
            (root / R.FREEZE_PATH).write_text(json.dumps(R.freeze_manifest(root)))
            self.assertEqual(R.verify_freeze(root), [])
            (root / "src/a.py").write_text("x = 2\n")
            self.assertTrue(any("changed" in p and "src/a.py" in p for p in R.verify_freeze(root)))
            (root / "src/a.py").write_text("x = 1\n")
            (root / "results/task3/train/dqn_s0/checkpoints/best_val.pt").write_bytes(b"other")
            self.assertTrue(any("best_val.pt" in p for p in R.verify_freeze(root)))
            (root / "results/task3/train/dqn_s0/checkpoints/best_val.pt").write_bytes(b"weights")
            (root / "src/new.py").write_text("y = 1\n")
            self.assertTrue(any("new file" in p for p in R.verify_freeze(root)))

    def test_final_split_requires_a_clean_freeze_and_every_held_out_use_is_logged(self):
        with tempfile.TemporaryDirectory() as t:
            root = self.make_repo(t)
            with self.assertRaises(R.SplitAccessError):
                R.claim_split(root, "final", "x")                      # no freeze manifest yet
            (root / "protocol").mkdir(); (root / R.FREEZE_PATH).write_text(json.dumps(R.freeze_manifest(root)))
            R.claim_split(root, "final", "x")                          # frozen and unchanged: allowed
            (root / "src/a.py").write_text("x = 3\n")
            with self.assertRaises(R.SplitAccessError):
                R.claim_split(root, "final", "x")                      # code changed after the freeze: refused
            R.claim_split(root, "val", "x"); R.claim_split(root, "test", "y"); R.claim_split(root, "pilot", "z")
            lines = [json.loads(l) for l in (root / "results/test_access.jsonl").read_text().splitlines()]
            self.assertEqual([l["split"] for l in lines], ["final", "test"])   # val/pilot are not held-out; the refused attempt is not logged

    def test_method_spec_parsing_and_tags(self):
        self.assertEqual(parse_method("assured")["variant"], "full")
        self.assertEqual(parse_method("assured-no_ood@90")["pct"], 90.0)
        self.assertEqual(method_tag("assured-no_stop@95", 3), "assured-no_stop_p95_s3")
        self.assertEqual(method_tag("assured", 0), "assured_p95_s0")
        self.assertEqual(method_tag("dqn_shield", 2), "dqn_shield_s2")
        self.assertEqual(method_tag("astar", 5), "astar")
        for bad in ("assured-bogus", "dqn@95", "nonsense"):
            with self.assertRaises(ValueError):
                parse_method(bad)


if __name__ == "__main__":
    unittest.main()
