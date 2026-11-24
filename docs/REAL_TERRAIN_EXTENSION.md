# Real-terrain extension (proposed amendment A2): scope and plan

Status: **scoped, not started**. It needs public Mars data to be downloaded, which hasn't been approved yet. Nothing here
changes the v1.1 or A1 results.

## Goal
Answer the reviewer question "procedural maps only?" with an **evaluation-only** condition built from real Mars orbital
terrain. There is no retraining and no threshold changes: the frozen ensembles, thresholds, monitor and planners are run
unchanged. This makes it an out-of-distribution transfer test, and it keeps the existing freeze valid.

## Data
| Source | Use | Format / access |
|---|---|---|
| **HiRISE DTMs** (University of Arizona / NASA PDS; ~1 m/px elevation for sites such as Jezero and Gale crater) | primary: slope and roughness → terrain class grid | PDS `.IMG` (32-bit float raster + label) per site, typically tens to hundreds of MB each |
| AI4Mars (Swan et al., CVPRW 2021; NASA Open Data, Hugging Face mirror) | secondary: justify the class mapping and the sensor-noise model (soil / bedrock / sand / big rock) | rover-view images + masks; **not** top-down maps, so not used to build grids |

### Exact files (checked 2026-11-24 with HTTP HEAD; nothing downloaded yet)
Base URL: `https://hirise-pds.lpl.arizona.edu/PDS/DTM/`

| Site (rover) | File | Size | Path under base URL |
|---|---|---|---|
| Jezero crater (Perseverance) | `DTEEC_023524_1985_023379_1985_U01.IMG` | 700,271,460 B (700 MB) | `ESP/ORB_023500_023599/ESP_023524_1985_ESP_023379_1985/` |
| Gale crater floor / Mt Sharp (Curiosity) | `DTEEC_009505_1755_009571_1755_U01.IMG` | 830,489,472 B (830 MB) | `PSP/ORB_009500_009599/PSP_009505_1755_PSP_009571_1755/` |
| Victoria crater, Meridiani (Opportunity) | `DTEEC_001414_1780_001612_1780_U01.IMG` | 8,671,620 B (8.7 MB) | `PSP/ORB_001400_001499/PSP_001414_1780_PSP_001612_1780/` |

Total about 1.54 GB (308 GB free on disk). Files are stored in `data/hirise/` and git-ignored; only the derived tile `.npz` and
its SHA-256 hash are committed. Format: PDS3 `.IMG` with an embedded text label (32-bit float elevations, metres, with a
missing-data constant), read with numpy `memmap`, so no GDAL is needed. The server supports HTTP range requests, so if
bandwidth is a problem a row band of each DTM can be fetched instead of the full file.

Recommended scope: these 3 sites. Taking 32×32 tiles at a 2–4 m cell size gives several hundred candidate maps.

## Map construction (fixed before looking at any results)
1. Resample the DTM to cell size *c* (fixed: 2 m). Compute per-cell slope (degrees) and roughness (std. of the
   detrended elevation inside the cell).
2. Class rule (fixed a priori, from published rover traversability ranges; document the source when writing it up):
   obstacle if slope > 25° or roughness above the 97th percentile of the site; rock if slope 15–25°; sand if slope < 5°
   and roughness < 20th percentile (smooth, low-lying fill); normal otherwise.
3. Tile into non-overlapping 32×32 maps. Keep tiles whose start/goal corners are traversable, whose goal is reachable,
   and whose nominal optimal cost is ≤ 0.6 × battery (the same acceptance rule as the simulator).
4. Use the ID sensor/slip/energy parameters, so only the *terrain structure* differs. A second preset with combined-shift
   physics is optional.
5. Fix the tile list by hashing it before any method is run. Split the tiles 50/50 into `real_pilot` (debugging only)
   and `real_final` (confirmatory).

## Code changes (small)
* `src/environment/procgen.py`: add an `external_grid` option, so `AdvancedEnv.reset(seed)` loads tile *seed* from a
  `.npz` instead of generating terrain. Start and goal stay at the corners.
* `configs/sim32_real_hirise.yaml`: the preset.
* `scripts/build_real_maps.py`: implements steps 1–5 above and writes the tile `.npz` and its hash.
* Tests: tile loading is deterministic; the leakage tests still pass with external grids.

## Pre-registered analysis (to be written as `protocol/amendment_A2_real_terrain.json` before any run)
Same methods, seeds and statistics as v1.1. The primary comparisons are assured@95 vs A*+monitor and assured@95 vs ensemble on
success and unsafe moves, with Holm correction across the real-terrain presets.

## Effort and risk
About 1–2 weeks: data handling 2–3 days, map construction 2 days, runs under 1 day, write-up 2 days. The main risk is
that the class mapping is a modelling choice, so the paper must present it as *terrain structure from real elevation
data*, not as real traversability. The added novelty is moderate: mainly credibility and external validity, not a new
mechanism.
