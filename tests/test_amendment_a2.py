"""Amendment A2: PDS3 DTM reader, pre-registered class rule, and evaluation-only loading of real-terrain tiles."""
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path

import numpy as np

from src.config import load_config
from src.environment import terrain as T
from src.environment.real_terrain import MISSING, candidate_tiles, classify, load_dtm, read_label, to_cells

ROOT = Path(__file__).resolve().parents[1]


def _write_img(path, z, scale=1.0):
    rec = z.shape[1] * 4
    k = 200 // rec + 30                                    # label records: comfortably larger than the label text
    label = (f"PDS_VERSION_ID = PDS3\nRECORD_TYPE = FIXED_LENGTH\nRECORD_BYTES = {rec}\nFILE_RECORDS = {z.shape[0] + k}\n"
             f"^IMAGE = {k + 1}\nOBJECT = IMAGE\n  LINES = {z.shape[0]}\n  LINE_SAMPLES = {z.shape[1]}\n  SAMPLE_BITS = 32\n"
             f"  SAMPLE_TYPE = PC_REAL\n  SCALING_FACTOR = 1.0\n  OFFSET = 0.0\nEND_OBJECT = IMAGE\n"
             f"OBJECT = IMAGE_MAP_PROJECTION\n  MAP_SCALE = {scale} <METERS/PIXEL>\nEND_OBJECT = IMAGE_MAP_PROJECTION\nEND\n")
    assert len(label) <= k * rec
    raw = label.encode().ljust(k * rec, b" ")
    Path(path).write_bytes(raw + z.astype("<f4").tobytes())


class TestA2(unittest.TestCase):
    def test_reader_and_block_average(self):
        z = np.arange(8 * 6, dtype=np.float32).reshape(8, 6)
        z[0, 0] = MISSING
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "t.IMG"
            _write_img(p, z)
            self.assertEqual(read_label(p)["MAP_SCALE"], "1.0")         # label continues past END_OBJECT lines
            zz, ms, sc = load_dtm(p)
            np.testing.assert_array_equal(np.asarray(zz)[1:], z[1:])
            cells = to_cells(zz, ms, 2.0, sc)
        self.assertEqual(cells.shape, (4, 3))
        self.assertTrue(np.isnan(cells[0, 0]))                         # any missing pixel invalidates the cell
        self.assertAlmostEqual(cells[1, 1], z[2:4, 2:4].mean())

    def test_class_rule(self):
        slope = np.array([[2.0, 10.0, 20.0, 30.0, 2.0]]); rough = np.array([[0.0, 0.5, 0.5, 0.5, 9.0]])
        g = classify(slope, rough, p97=1.0, p20=0.1)
        self.assertEqual(g.tolist(), [[T.SAND, T.NORMAL, T.ROCK, T.OBSTACLE, T.OBSTACLE]])

    def test_candidate_tiles_need_full_validity(self):
        g = np.zeros((64, 64), dtype=np.int64); g[40, 40] = -1
        self.assertEqual(len(candidate_tiles(g)), 3)

    def test_env_loads_tile_by_seed_and_keeps_it_hidden(self):
        tiles = ROOT / "data/real_tiles/hirise_tiles.npz"
        if not tiles.exists():
            self.skipTest("tile file not built yet")
        from src.evaluation.evaluator import make_env
        cfg = load_config(ROOT / "configs/sim32_real_hirise.yaml")
        env, ev = make_env(cfg.env, 0)
        z = np.load(tiles)
        s = int(z["seeds"][0])
        o1 = env.reset(seed=s); g1 = ev.grid.copy()
        o2 = env.reset(seed=s)
        np.testing.assert_array_equal(o1, o2); np.testing.assert_array_equal(g1, ev.grid)
        expect = z["grids"][0].astype(np.int64); expect[:3, :3] = T.NORMAL; expect[-3:, -3:] = T.NORMAL
        np.testing.assert_array_equal(g1, expect)
        self.assertFalse(any("tile" in k for k in vars(env) if not k.startswith("_")))
        with self.assertRaises(ValueError):
            env.reset()


if __name__ == "__main__":
    unittest.main()
