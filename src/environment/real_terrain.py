"""Amendment A2: 32x32 terrain tiles from HiRISE DTMs (generator side; never imported by agents or onboard components).

Implements exactly the map construction pre-registered in protocol/amendment_A2_real_terrain.json.
"""
from __future__ import annotations

import re
from pathlib import Path

import numpy as np

from src.environment.terrain import NORMAL, OBSTACLE, ROCK, SAND

MISSING = np.frombuffer(bytes.fromhex("FBFF7FFF"), "<f4")[0]   # 16#FF7FFFFB# as little-endian PC_REAL


def read_label(path) -> dict:
    """Minimal PDS3 embedded-label parser for the keys we need."""
    head = Path(path).open("rb").read(65536).decode("latin-1")
    m_end = re.search(r"^END\s*$", head, re.M)          # the label ends at a line that is exactly END
    head = head[:m_end.end()] if m_end else head
    out = {}
    for key in ("RECORD_BYTES", "LABEL_RECORDS", "^IMAGE", "LINES", "LINE_SAMPLES", "SAMPLE_BITS", "SAMPLE_TYPE", "MAP_SCALE",
                "SCALING_FACTOR", "OFFSET"):
        m = re.search(r"^\s*" + re.escape(key) + r"\s*=\s*([^\s<]+)", head, re.M)
        if m:
            out[key] = m.group(1)
    return out


def load_dtm(path):
    """(float32 memmap of raw samples, map scale in m/pixel, (scaling factor, offset)). Missing = MISSING constant."""
    lab = read_label(path)
    if lab.get("SAMPLE_TYPE") != "PC_REAL" or lab.get("SAMPLE_BITS") != "32":
        raise ValueError(f"unsupported sample type in {path}: {lab}")
    rec, ptr = int(lab["RECORD_BYTES"]), int(lab["^IMAGE"])
    lines, samples = int(lab["LINES"]), int(lab["LINE_SAMPLES"])
    z = np.memmap(path, dtype="<f4", mode="r", offset=(ptr - 1) * rec, shape=(lines, samples))
    scale = float(lab.get("SCALING_FACTOR", 1.0)); off = float(lab.get("OFFSET", 0.0))
    return z, float(lab["MAP_SCALE"]), (scale, off)


def to_cells(z, map_scale: float, cell_m: float = 2.0, scaling=(1.0, 0.0), chunk: int = 2048) -> np.ndarray:
    """Block-average to `cell_m` cells; NaN where any pixel of the block is missing. Streams over row chunks."""
    f = max(1, int(round(cell_m / map_scale)))
    L, S = (z.shape[0] // f) * f, (z.shape[1] // f) * f
    rows = []
    step = max(f, (chunk // f) * f)
    for r0 in range(0, L, step):
        b = np.asarray(z[r0:min(r0 + step, L), :S], dtype=np.float64)
        bad = (b == MISSING) | ~np.isfinite(b) | (b < -1e30)
        b = np.where(bad, np.nan, b * scaling[0] + scaling[1])
        b = b.reshape(b.shape[0] // f, f, S // f, f)
        rows.append(b.mean(axis=(1, 3)))          # NaN propagates: any missing pixel -> invalid cell
    return np.vstack(rows)


def slope_roughness(zc: np.ndarray, cell_m: float = 2.0):
    gy, gx = np.gradient(zc, cell_m)
    slope = np.degrees(np.arctan(np.hypot(gx, gy)))
    p = np.pad(zc, 1, mode="edge")
    n, m = zc.shape
    mean3 = sum(p[i:i + n, j:j + m] for i in range(3) for j in range(3)) / 9.0
    return slope, np.abs(zc - mean3)


def classify(slope: np.ndarray, rough: np.ndarray, p97: float, p20: float) -> np.ndarray:
    """Pre-registered rule. Returns int grid with NORMAL/SAND/ROCK/OBSTACLE; -1 where invalid."""
    g = np.full(slope.shape, NORMAL, dtype=np.int64)
    g[(slope < 5.0) & (rough < p20)] = SAND
    g[(slope > 15.0) & (slope <= 25.0)] = ROCK
    g[(slope > 25.0) | (rough > p97)] = OBSTACLE
    g[~(np.isfinite(slope) & np.isfinite(rough))] = -1
    return g


def site_grid(path, cell_m: float = 2.0) -> tuple[np.ndarray, dict]:
    z, ms, sc = load_dtm(path)
    zc = to_cells(z, ms, cell_m, sc)
    slope, rough = slope_roughness(zc, cell_m)
    interior = np.isfinite(rough) & np.isfinite(slope)
    p97, p20 = float(np.percentile(rough[interior], 97)), float(np.percentile(rough[interior], 20))
    g = classify(slope, rough, p97, p20)
    return g, {"map_scale": ms, "cells": list(zc.shape), "valid_cells": int(interior.sum()), "rough_p97": p97, "rough_p20": p20}


def candidate_tiles(g: np.ndarray, size: int = 32):
    """Non-overlapping, fully valid tiles, row-major from the origin: [(row, col, tile)]."""
    out = []
    for r in range(0, g.shape[0] - size + 1, size):
        for c in range(0, g.shape[1] - size + 1, size):
            t = g[r:r + size, c:c + size]
            if (t >= 0).all():
                out.append((r, c, t.copy()))
    return out
