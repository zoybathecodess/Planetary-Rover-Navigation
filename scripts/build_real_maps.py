"""Amendment A2: build the real-terrain tile set from the three HiRISE DTMs, exactly as pre-registered.

  python3 scripts/build_real_maps.py            -> data/real_tiles/hirise_tiles.npz + hirise_tiles.json (stats + sha256)
"""
from _common import ROOT  # noqa: F401

import hashlib
import io
import json

import numpy as np

from src.environment import procgen as G
from src.environment import terrain as T
from src.environment.real_terrain import candidate_tiles, site_grid

SITES = [("victoria", "DTEEC_001414_1780_001612_1780_U01.IMG"), ("jezero", "DTEEC_023524_1985_023379_1985_U01.IMG"),
         ("gale", "DTEEC_009505_1755_009571_1755_U01.IMG")]
SIZE, BATTERY, FRAC, PER_SITE, FINAL_CAP = 32, 250, 0.6, 300, 500
REF = G.energy_lut((1, 3, 5)); TRUE_ID = G.energy_lut((1, 3, 5))
OUT = ROOT / "data/real_tiles"


def accept(t):
    start, goal = (0, 0), (SIZE - 1, SIZE - 1)
    G.clear_blocks(t, start, goal)
    ref = G.dijkstra_lut(t, start, REF)[goal]
    if ref >= T.INF or ref > FRAC * BATTERY:
        return False
    return G.dijkstra_lut(t, start, TRUE_ID)[goal] <= BATTERY


def main():
    kept, stats = [], {}
    for site, fname in SITES:
        g, info = site_grid(ROOT / "data/hirise" / fname)
        cands = candidate_tiles(g, SIZE)
        ok = [(r, c, t) for r, c, t in cands if accept(t)]
        order = np.random.default_rng(2026).permutation(len(ok))
        sel = [ok[i] for i in order[:PER_SITE]]
        valid = g[g >= 0]
        comp = {k: float(np.mean(valid == v)) for k, v in (("normal", T.NORMAL), ("sand", T.SAND), ("rock", T.ROCK), ("obstacle", T.OBSTACLE))}
        stats[site] = {**info, "candidates": len(cands), "accepted": len(ok), "kept": len(sel), "composition": comp}
        print(f"{site:9} cells {info['cells']}  candidates {len(cands):5}  accepted {len(ok):5}  kept {len(sel):4}  "
              f"composition " + " ".join(f"{k} {v:.2f}" for k, v in comp.items()))
        kept += [(site, r, c, t) for r, c, t in sel]
    order = np.random.default_rng(2027).permutation(len(kept))
    kept = [kept[i] for i in order]
    half = len(kept) // 2
    pilot, final = kept[:half], kept[half:][:FINAL_CAP]
    rows = [(70000 + i, "real_final", *k) for i, k in enumerate(final)] + [(75000 + i, "real_pilot", *k) for i, k in enumerate(pilot)]
    OUT.mkdir(parents=True, exist_ok=True)
    buf = io.BytesIO()
    np.savez_compressed(buf, seeds=np.array([r[0] for r in rows]), split=np.array([r[1] for r in rows]),
                        site=np.array([r[2] for r in rows]), row=np.array([r[3] for r in rows]), col=np.array([r[4] for r in rows]),
                        grids=np.stack([r[5] for r in rows]).astype(np.int8))
    (OUT / "hirise_tiles.npz").write_bytes(buf.getvalue())
    sha = hashlib.sha256(buf.getvalue()).hexdigest()
    by_split = {s: {site: sum(1 for r in rows if r[1] == s and r[2] == site) for site, _ in SITES} for s in ("real_final", "real_pilot")}
    meta = {"amendment": "A2", "sha256": sha, "n_final": len(final), "n_pilot": len(pilot), "by_split": by_split, "sites": stats}
    (OUT / "hirise_tiles.json").write_text(json.dumps(meta, indent=2))
    print(json.dumps({"sha256": sha, "n_final": len(final), "n_pilot": len(pilot), "by_split": by_split}, indent=1))


if __name__ == "__main__":
    main()
