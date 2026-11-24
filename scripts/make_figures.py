"""Publication figures (Task 9). Reads only saved logs / analysis CSVs, except Fig. 2, which records one illustrative episode
on a PILOT map (debug split, never a result).

  python3 scripts/make_figures.py                     # all figures -> paper/figures/*.pdf (+ .png previews)
Figures: fig1_architecture, fig2_episode, fig3_success_unsafe, fig4_energy, fig5_interventions, fig6_ablation,
fig7_sensitivity, fig8_h3, fig9_a3 (the last two only if the amendment runs exist).
"""
from _common import ROOT  # noqa: F401

import csv
import json
import math
from collections import defaultdict
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

from src.evaluation.stats import mean_ci, wilson  # noqa: E402

OUT = ROOT / "paper" / "figures"
MAIN = ROOT / "results/phase2/phase2/analysis/final/metrics_by_seed.csv"
H3 = ROOT / "results/phase2/h3"
CONDS = ["id", "terrain_shift", "sensor_shift", "dynamics_shift", "combined_shift"]
CLAB = {"id": "ID", "terrain_shift": "Terrain", "sensor_shift": "Sensor", "dynamics_shift": "Dynamics", "combined_shift": "Combined"}
MAIN_METHODS = [("astar", "A*"), ("astar_monitor", "A*+monitor"), ("dqn", "DQN"), ("dqn_shield", "DQN+shield"),
                ("ppo_shield", "PPO+shield"), ("ens", "Ensemble"), ("assured-unc_only@95", "Unc.-gated"), ("assured@95", "Assured (ours)")]
# colour-blind-safe palette (Okabe–Ito), fixed per method across every figure
COL = {"astar": "#000000", "astar_monitor": "#7f7f7f", "dqn": "#E69F00", "dqn_shield": "#D55E00", "ppo_shield": "#CC79A7",
       "ens": "#56B4E9", "assured-unc_only@95": "#009E73", "assured@95": "#0072B2", "assured-no_stop@95": "#5fa8d3"}

plt.rcParams.update({"font.family": "serif", "font.serif": ["STIXGeneral", "DejaVu Serif"], "mathtext.fontset": "stix", "font.size": 8, "axes.titlesize": 8, "axes.labelsize": 8, "legend.fontsize": 6.5,
                     "xtick.labelsize": 7, "ytick.labelsize": 7, "axes.spines.top": False, "axes.spines.right": False,
                     "savefig.bbox": "tight", "savefig.pad_inches": 0.02, "pdf.fonttype": 42})
COLW, TEXTW = 3.5, 7.16       # IEEE column / text width, inches


def load_by_seed(path):
    d = defaultdict(lambda: defaultdict(list))
    with open(path) as f:
        for r in csv.DictReader(f):
            d[(r["condition"], r["method"])]["rows"].append(r)
    return d


def stat(d, cond, method, metric):
    rows = d[(cond, method)]["rows"]
    if not rows:
        return math.nan, math.nan, math.nan
    vals = [float(r[metric]) if r[metric] not in ("", "nan") else math.nan for r in rows]
    if len(rows) == 1:                       # seedless method (A*): Wilson interval for proportions, none otherwise
        v, n = vals[0], int(rows[0]["n_episodes"])
        if metric in ("success", "safe_stop_rate", "depleted_rate"):
            lo, hi = wilson(round(v * n), n)
            return v, v - lo, hi - v
        return v, 0.0, 0.0
    c = mean_ci(vals)
    return c["mean"], c["mean"] - c["lo"], c["hi"] - c["mean"]


def save(fig, name):
    OUT.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT / f"{name}.pdf"); fig.savefig(OUT / f"{name}.png", dpi=220)
    plt.close(fig)
    print("  ->", OUT / f"{name}.pdf")


def grouped(ax, d, methods, metric, ylabel, log=False):
    n = len(methods)
    w = 0.8 / n
    x = np.arange(len(CONDS))
    for i, (m, lab) in enumerate(methods):
        s = [stat(d, c, m, metric) for c in CONDS]
        ax.bar(x + (i - (n - 1) / 2) * w, [v[0] for v in s], w, yerr=[[v[1] for v in s], [v[2] for v in s]],
               color=COL.get(m, "#999"), label=lab, error_kw={"lw": 0.6, "capsize": 1.2}, edgecolor="white", linewidth=0.3)
    ax.set_xticks(x, [CLAB[c] for c in CONDS], fontsize=6.5); ax.set_ylabel(ylabel)
    if log:
        ax.set_yscale("log")
    ax.grid(axis="y", lw=0.3, alpha=0.5)


# ------------------------------------------------------------------ Fig. 1 architecture
def fig1():
    """Black-and-white decision flowchart (single column)."""
    from matplotlib.patches import FancyArrowPatch, Polygon, Rectangle
    fig, ax = plt.subplots(figsize=(COLW, 3.1))
    ax.set_xlim(0, 100); ax.set_ylim(0, 132); ax.axis("off")
    kw = dict(fc="white", ec="black", lw=0.8)

    def box(x0, x1, y0, y1, text):
        ax.add_patch(Rectangle((x0, y0), x1 - x0, y1 - y0, **kw))
        ax.text((x0 + x1) / 2, (y0 + y1) / 2, text, ha="center", va="center", fontsize=7)

    def diamond(cx, cy, w, h, text):
        ax.add_patch(Polygon([(cx - w, cy), (cx, cy + h), (cx + w, cy), (cx, cy - h)], closed=True, **kw))
        ax.text(cx, cy, text, ha="center", va="center", fontsize=7)

    def arrow(p0, p1, label=None, lx=0, ly=0):
        ax.add_patch(FancyArrowPatch(p0, p1, arrowstyle="-|>", mutation_scale=8, lw=0.8, color="black", shrinkA=0, shrinkB=0))
        if label:
            ax.text((p0[0] + p1[0]) / 2 + lx, (p0[1] + p1[1]) / 2 + ly, label, ha="center", va="center", fontsize=6.5)

    box(30, 70, 121, 130, "Observation")
    box(28, 72, 104, 113, "Policy proposes action")
    box(1, 31, 84, 94, "Uncertainty")
    box(35, 65, 84, 94, "Novelty (OOD)")
    box(69, 99, 84, 94, "Safety rules")
    diamond(50, 67, 14, 9, "All pass?")
    box(71, 99.5, 62, 72, "Execute action")
    box(30, 70, 44, 53, "Fallback planner")
    diamond(50, 28, 14, 9, "Safe move?")
    box(71, 99.5, 23, 33, "Execute move")
    box(30, 70, 3, 12, "Safe stop")
    arrow((50, 121), (50, 113))
    for x in (16, 50, 84):
        arrow((50, 104), (x, 94))
        arrow((x, 84), (50, 76))
    arrow((64, 67), (71, 67), "yes", ly=4.2)
    arrow((50, 58), (50, 53), "no", lx=4)
    arrow((50, 44), (50, 37))
    arrow((64, 28), (71, 28), "yes", ly=4.2)
    arrow((50, 19), (50, 12), "no", lx=4)
    save(fig, "fig1_architecture")


# ------------------------------------------------------------------ Fig. 2 example episode (pilot map)
def fig2():
    from src.config import load_config
    from src.evaluation.evaluator import make_env
    from src.evaluation.experiment import build_method
    from src.evaluation.replay import plot_episode, record_episode
    from src.evaluation.reproducibility import SPLIT_OFFSET
    seed = SPLIT_OFFSET["pilot"] + 3
    cfg = load_config(ROOT / "configs/sim32_terrain_shift.yaml")
    env, ev = make_env(cfg.env, 0)
    pol = build_method("assured@95", 0, ROOT, keep_log=True)
    pol.attach(env.explored_map, env.max_battery)
    rec = record_episode(env, ev, pol, seed)
    log = pol.log
    first_fb = next((i for i, d in enumerate(log) if d["source"] != "policy"), len(log))
    fig = plt.figure(figsize=(TEXTW, 2.6))
    fig = plot_episode(rec, None, t=first_fb, fig=fig)
    for a in fig.axes:
        for sp in a.spines.values():
            sp.set_visible(False)
    ax0 = fig.axes[0]
    for d, s in zip(log, rec["steps"]):
        if d["source"] != "policy":
            ax0.plot(s["from"][1], s["from"][0], "x" if d["source"] == "fallback" else "X", c="#D55E00", ms=3.5, mew=0.9)
    n_fb = sum(d["source"] == "fallback" for d in log)
    fig.suptitle(f"Illustrative pilot map (terrain shift), assured@95, shown at step {first_fb} (first intervention: "
                 f"{', '.join(log[first_fb]['reasons'])}). Episode outcome: {rec['reason']}, {len(rec['steps'])} steps, "
                 f"{n_fb} fallback steps (×).", fontsize=6.5)
    for a in fig.axes:
        a.title.set_fontsize(7)
        for t in a.texts:
            t.set_fontsize(5)
    save(fig, "fig2_episode")


# ------------------------------------------------------------------ Fig. 3–7 from the frozen campaign
def fig3(d):
    fig, ax = plt.subplots(1, 2, figsize=(TEXTW, 2.1))
    grouped(ax[0], d, MAIN_METHODS, "success", "Mission success rate")
    ax[0].set_ylim(0.4, 1.02)
    grouped(ax[1], d, MAIN_METHODS, "unsafe", "Unsafe moves / episode (log)", log=True)
    ax[0].set_title("(a) Success"); ax[1].set_title("(b) Unsafe-action exposure")
    h, l = ax[0].get_legend_handles_labels()
    fig.legend(h, l, ncol=8, loc="upper center", bbox_to_anchor=(0.5, 1.07), frameon=False, handlelength=1.0, columnspacing=0.8)
    save(fig, "fig3_success_unsafe")


def fig4(d):
    fig, ax = plt.subplots(1, 2, figsize=(TEXTW, 2.1))
    grouped(ax[0], d, MAIN_METHODS, "energy_used", "Energy used / episode (sim. units)")
    grouped(ax[1], d, MAIN_METHODS, "depleted_rate", "Battery-depletion rate")
    ax[0].set_title("(a) Energy consumption"); ax[1].set_title("(b) Episodes ending in battery depletion")
    h, l = ax[0].get_legend_handles_labels()
    fig.legend(h, l, ncol=8, loc="upper center", bbox_to_anchor=(0.5, 1.07), frameon=False, handlelength=1.0, columnspacing=0.8)
    save(fig, "fig4_energy")


def fig5(d):
    ms = [("astar_monitor", "A*+monitor"), ("assured-unc_only@95", "Unc.-gated"), ("assured@95", "Assured"), ("assured-no_stop@95", "Assured, no stop")]
    fig, ax = plt.subplots(1, 3, figsize=(TEXTW, 1.95))
    for a, (metric, lab) in zip(ax, [("intervention_rate", "(a) Intervention rate / decision"), ("fallback_success", "(b) Fallback success"),
                                     ("safe_stop_rate", "(c) Safe-stop rate")]):
        grouped(a, d, ms, metric, "")
        a.set_title(lab)
        a.tick_params(axis="x", rotation=30)
    h, l = ax[0].get_legend_handles_labels()
    fig.legend(h, l, ncol=4, loc="upper center", bbox_to_anchor=(0.5, 1.08), frameon=False)
    save(fig, "fig5_interventions")


def fig6(d):
    abl = [("ens", "Ensemble only"), ("assured-ood_only@95", "OOD only"), ("assured-unc_only@95", "Unc. only"),
           ("assured-monitor_only@95", "Monitor only"), ("assured-no_ood@95", "Full − OOD"), ("assured-no_unc@95", "Full − unc."),
           ("assured-no_monitor@95", "Full − monitor"), ("assured@95", "Full")]
    fig, ax = plt.subplots(1, 2, figsize=(TEXTW, 2.4))
    for a, metric, lab in ((ax[0], "success", "Success rate"), (ax[1], "unsafe", "Unsafe moves / episode (log)")):
        y = np.arange(len(abl))
        for j, c in enumerate(CONDS):
            s = [stat(d, c, m, metric) for m, _ in abl]
            a.errorbar([v[0] for v in s], y + (j - 2) * 0.13, xerr=[[v[1] for v in s], [v[2] for v in s]], fmt="o", ms=2.2,
                       lw=0.6, label=CLAB[c], color=["#000", "#E69F00", "#56B4E9", "#009E73", "#D55E00"][j])
        a.set_yticks(y, [l for _, l in abl] if a is ax[0] else [""] * len(abl)); a.set_xlabel(lab); a.grid(axis="x", lw=0.3, alpha=0.5)
        if metric == "unsafe":
            a.set_xscale("log")
    ax[0].set_title("(a) Success"); ax[1].set_title("(b) Unsafe-action exposure")
    h, l = ax[0].get_legend_handles_labels()
    fig.legend(h, l, ncol=5, loc="upper center", bbox_to_anchor=(0.55, 1.05), frameon=False)
    save(fig, "fig6_ablation")


def fig7(d):
    fig, ax = plt.subplots(1, 3, figsize=(TEXTW, 1.8))
    for a, (metric, lab) in zip(ax, [("success", "Success"), ("unsafe", "Unsafe / episode"), ("intervention_rate", "Intervention rate")]):
        for j, c in enumerate(CONDS):
            s = [stat(d, c, f"assured@{p}", metric) for p in (90, 95, 99)]
            a.errorbar([90, 95, 99], [v[0] for v in s], yerr=[[v[1] for v in s], [v[2] for v in s]], marker="o", ms=2.5, lw=0.8,
                       capsize=1.5, label=CLAB[c], color=["#000", "#E69F00", "#56B4E9", "#009E73", "#D55E00"][j])
        a.set_xticks([90, 95, 99]); a.set_xlabel("Threshold percentile (ID val.)"); a.set_title(lab); a.grid(lw=0.3, alpha=0.5)
    h, l = ax[0].get_legend_handles_labels()
    fig.legend(h, l, ncol=5, loc="upper center", bbox_to_anchor=(0.5, 1.1), frameon=False)
    save(fig, "fig7_sensitivity")


def fig8():
    p = H3 / "analysis/final/h3_paired.csv"
    if not p.exists():
        print("  (no amendment-A1 analysis yet: skipping fig8_h3)")
        return
    rows = list(csv.DictReader(open(p)))
    want = [("energy_feasible_intervention_rate", "Δ energy-feasible\nintervention rate"), ("fallback_success", "Δ fallback success"),
            ("energy_used", "Δ energy used")]
    fig, ax = plt.subplots(1, 3, figsize=(TEXTW, 1.9))
    comps = sorted({r["comparison"] for r in rows})
    for a, (metric, lab) in zip(ax, want):
        for k, comp in enumerate(comps):
            rr = [next(r for r in rows if r["comparison"] == comp and r["metric"] == metric and r["condition"] == c) for c in CONDS]
            x = np.arange(len(CONDS)) + (k - 0.5) * 0.25
            m = np.array([float(r["diff"]) for r in rr])
            lo, hi = np.array([float(r["lo"]) for r in rr]), np.array([float(r["hi"]) for r in rr])
            a.errorbar(x, m, yerr=[m - lo, hi - m], fmt="o", ms=2.8, lw=0.8, capsize=1.5,
                       color=["#0072B2", "#5fa8d3"][k], label="with safe stop" if "no stop" not in comp else "no safe stop")
            for xi, r in zip(x, rr):
                if float(r["p_holm"]) < 0.05:
                    a.text(xi, float(r["hi"]), "*", ha="center", va="bottom", fontsize=7)
        a.axhline(0, lw=0.5, color="#555"); a.set_xticks(range(len(CONDS)), [CLAB[c] for c in CONDS], rotation=30)
        a.set_title(lab + "\n(battery-aware − energy-blind)", fontsize=7); a.grid(axis="y", lw=0.3, alpha=0.5)
    h, l = ax[0].get_legend_handles_labels()
    fig.legend(h, l, ncol=2, loc="upper center", bbox_to_anchor=(0.5, 1.22), frameon=False)
    save(fig, "fig8_h3")


def fig9():
    p = ROOT / "results/phase2/a3/analysis/final/a3_paired.csv"
    if not p.exists():
        print("  (no amendment-A3 analysis yet: skipping fig9_a3)")
        return
    rows = list(csv.DictReader(open(p)))
    want = [("success", "(a) Δ success"), ("unsafe", "(b) Δ unsafe moves / episode")]
    comps = [("action-OOD vs raw-OOD (full system)", "action-cond. − raw OOD gate", "black"),
             ("action-OOD vs no OOD (full system)", "action-cond. − no OOD gate", "#888888")]
    fig, ax = plt.subplots(1, 2, figsize=(COLW, 1.75))
    for a, (metric, lab) in zip(ax, want):
        for k, (comp, clab, col) in enumerate(comps):
            rr = [next(r for r in rows if r["comparison"] == comp and r["metric"] == metric and r["condition"] == c) for c in CONDS]
            x = np.arange(len(CONDS)) + (k - 0.5) * 0.25
            m = np.array([float(r["diff"]) for r in rr]); lo = np.array([float(r["lo"]) for r in rr]); hi = np.array([float(r["hi"]) for r in rr])
            a.errorbar(x, m, yerr=[m - lo, hi - m], fmt="o" if k == 0 else "s", ms=2.6, lw=0.8, capsize=1.5, color=col, label=clab)
            for xi, r in zip(x, rr):
                if float(r["p_holm"]) < 0.05:
                    a.text(xi, max(float(r["hi"]), float(r["diff"])), "*", ha="center", va="bottom", fontsize=7)
        a.axhline(0, lw=0.5, color="#555"); a.set_xticks(range(len(CONDS)), [CLAB[c] for c in CONDS], rotation=40, fontsize=6)
        a.set_title(lab, fontsize=7); a.grid(axis="y", lw=0.3, alpha=0.5); a.tick_params(axis="y", labelsize=6)
    h, l = ax[0].get_legend_handles_labels()
    fig.legend(h, l, ncol=2, loc="upper center", bbox_to_anchor=(0.5, 1.13), frameon=False, fontsize=6)
    fig.tight_layout(w_pad=1.0)
    save(fig, "fig9_a3")


def fig10():
    p = ROOT / "data/real_tiles/hirise_tiles.npz"
    if not p.exists():
        print("  (no real-terrain tiles yet: skipping fig10_real_tiles)")
        return
    from matplotlib.colors import ListedColormap
    from src.evaluation.replay import TERRAIN_COLORS
    z = np.load(p)
    meta = json.loads((ROOT / "data/real_tiles/hirise_tiles.json").read_text())
    sites = [("victoria", "Victoria crater (Opportunity)"), ("jezero", "Jezero crater (Perseverance)"), ("gale", "Gale crater (Curiosity)")]
    fig, ax = plt.subplots(1, 4, figsize=(TEXTW, 1.95), gridspec_kw={"width_ratios": [1, 1, 1, 1.25]})
    for a, (site, lab) in zip(ax, sites):
        i = next(k for k in range(len(z["seeds"])) if z["site"][k] == site and z["split"][k] == "real_final")
        a.imshow(z["grids"][i], cmap=ListedColormap(TERRAIN_COLORS), vmin=0, vmax=3, interpolation="nearest")
        a.set_title(f"{lab}\ntile {int(z['seeds'][i])}", fontsize=6.5); a.set_xticks([]); a.set_yticks([])
        for sp in a.spines.values():
            sp.set_visible(False)
    names = ["normal", "sand", "rock", "obstacle"]
    x = np.arange(len(sites) + 1)
    comps = [[meta["sites"][s]["composition"][k] for k in names] for s, _ in sites] + [[0.60, 0.15, 0.10, 0.15]]
    bottom = np.zeros(len(x))
    for j, k in enumerate(names):
        v = np.array([c[j] for c in comps])
        ax[3].bar(x, v, bottom=bottom, color=TERRAIN_COLORS[j], edgecolor="#333", lw=0.3, label=k); bottom += v
    ax[3].set_xticks(x, ["Vict.", "Jez.", "Gale", "Proc. ID"], fontsize=6); ax[3].set_ylabel("")
    ax[3].legend(fontsize=5.5, frameon=False, loc="upper left", bbox_to_anchor=(1.0, 1.0)); ax[3].set_title("Terrain composition\n(fraction of cells)", fontsize=6.5)
    save(fig, "fig10_real_tiles")


if __name__ == "__main__":
    d = load_by_seed(MAIN)
    fig1(); fig2(); fig3(d); fig4(d); fig5(d); fig6(d); fig7(d); fig8(); fig9(); fig10()
