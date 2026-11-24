"""Publication figures (Task 9). Reads only saved logs / analysis CSVs, except Fig. 2, which records one illustrative episode
on a PILOT map (debug split, never a result).

  python3 scripts/make_figures.py                     # all figures -> paper/figures/*.pdf (+ .png previews)
Figures: fig1_architecture, fig2_episode, fig3_success_unsafe, fig4_energy, fig5_interventions, fig6_ablation,
fig7_sensitivity, fig8_h3, fig9_a3, fig10_real_tiles, fig11_real_shift, fig12_trajectories.
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


def grouped(ax, d, methods, metric, ylabel, log=False, small=False):
    n = len(methods)
    w = 0.8 / n
    x = np.arange(len(CONDS))
    for i, (m, lab) in enumerate(methods):
        s = [stat(d, c, m, metric) for c in CONDS]
        ax.bar(x + (i - (n - 1) / 2) * w, [v[0] for v in s], w, yerr=[[v[1] for v in s], [v[2] for v in s]],
               color=COL.get(m, "#999"), label=lab, error_kw={"lw": 0.6, "capsize": 1.2}, edgecolor="white", linewidth=0.3)
    ax.set_xticks(x, [CLAB[c] for c in CONDS], fontsize=5.5 if small else 6.5, rotation=35 if small else 0)
    ax.set_ylabel(ylabel)
    if small:
        ax.tick_params(axis="y", labelsize=6); ax.yaxis.label.set_size(6.5)
    if log:
        ax.set_yscale("log")
    ax.grid(axis="y", lw=0.3, alpha=0.5)


# ------------------------------------------------------------------ Fig. 1 architecture
def fig1():
    """Black-and-white decision flowchart (full column width)."""
    from matplotlib.patches import FancyArrowPatch, Polygon, Rectangle
    fig, ax = plt.subplots(figsize=(COLW, 4.0))
    ax.set_xlim(0, 100); ax.set_ylim(0, 132); ax.axis("off")
    kw = dict(fc="white", ec="black", lw=1.0)
    fs = 9

    def box(x0, x1, y0, y1, text):
        ax.add_patch(Rectangle((x0, y0), x1 - x0, y1 - y0, **kw))
        ax.text((x0 + x1) / 2, (y0 + y1) / 2, text, ha="center", va="center", fontsize=fs)

    def diamond(cx, cy, w, h, text):
        ax.add_patch(Polygon([(cx - w, cy), (cx, cy + h), (cx + w, cy), (cx, cy - h)], closed=True, **kw))
        ax.text(cx, cy, text, ha="center", va="center", fontsize=fs)

    def arrow(p0, p1, label=None, lx=0, ly=0):
        ax.add_patch(FancyArrowPatch(p0, p1, arrowstyle="-|>", mutation_scale=10, lw=1.0, color="black", shrinkA=0, shrinkB=0))
        if label:
            ax.text((p0[0] + p1[0]) / 2 + lx, (p0[1] + p1[1]) / 2 + ly, label, ha="center", va="center", fontsize=fs - 1)

    box(28, 72, 121, 131, "Observation")
    box(22, 78, 104, 114, "Policy proposes action")
    box(0.5, 32, 83, 94, "Uncertainty")
    box(34.5, 65.5, 83, 94, "Novelty (OOD)")
    box(68, 99.5, 83, 94, "Safety rules")
    diamond(50, 66, 15, 9.5, "All pass?")
    box(72, 99.5, 61, 71, "Execute")
    box(26, 74, 42, 52, "Fallback planner")
    diamond(50, 26, 15, 9.5, "Safe move?")
    box(72, 99.5, 21, 31, "Execute")
    box(28, 72, 1, 11, "Safe stop")
    arrow((50, 121), (50, 114))
    for x in (16, 50, 84):
        arrow((50, 104), (x, 94))
        arrow((x, 83), (50, 75.5))
    arrow((65, 66), (72, 66), "yes", ly=4.5)
    arrow((50, 56.5), (50, 52), "no", lx=5)
    arrow((50, 42), (50, 35.5))
    arrow((65, 26), (72, 26), "yes", ly=4.5)
    arrow((50, 16.5), (50, 11), "no", lx=5)
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
    fig = plt.figure(figsize=(TEXTW, 1.85))
    fig = plot_episode(rec, None, t=first_fb, fig=fig)
    for a in fig.axes:
        for sp in a.spines.values():
            sp.set_visible(False)
    ax0 = fig.axes[0]
    for d, st in zip(log, rec["steps"]):
        if d["source"] != "policy":
            ax0.plot(st["from"][1], st["from"][0], "x", c="#D55E00", ms=4, mew=1.0)
    titles = ["(a) Ground truth and trajectory", "(b) Explored map (onboard belief)", "(c) 5x5 sensor readings"]
    for a, t in zip(fig.axes, titles):
        a.set_title(t, fontsize=7.5)
        for tx in a.texts:
            tx.set_fontsize(5)
    fig._suptitle.set_visible(False) if fig._suptitle else None
    save(fig, "fig2_episode")


# ------------------------------------------------------------------ Fig. 3–7 from the frozen campaign
def fig3(d):
    fig, ax = plt.subplots(1, 2, figsize=(TEXTW, 1.55))
    grouped(ax[0], d, MAIN_METHODS, "success", "Mission success rate")
    ax[0].set_ylim(0.4, 1.02)
    grouped(ax[1], d, MAIN_METHODS, "unsafe", "Unsafe moves / episode (log)", log=True)
    ax[0].set_title("(a) Success"); ax[1].set_title("(b) Unsafe-action exposure")
    h, l = ax[0].get_legend_handles_labels()
    fig.legend(h, l, ncol=8, loc="lower center", bbox_to_anchor=(0.5, 1.0), frameon=False, handlelength=1.0, columnspacing=0.8)
    save(fig, "fig3_success_unsafe")


def fig4(d):
    """Column width; colours as in Fig. 3 (shared legend)."""
    fig, ax = plt.subplots(1, 2, figsize=(COLW, 1.45))
    grouped(ax[0], d, MAIN_METHODS, "energy_used", "Energy / episode", small=True)
    grouped(ax[1], d, MAIN_METHODS, "depleted_rate", "Depletion rate", small=True)
    ax[0].set_title("(a) Energy used", fontsize=7); ax[1].set_title("(b) Battery depletion", fontsize=7)
    fig.tight_layout(w_pad=0.8)
    save(fig, "fig4_energy")


def fig5(d):
    ms = [("astar_monitor", "A*+monitor"), ("assured-unc_only@95", "Unc.-gated"), ("assured@95", "Assured"), ("assured-no_stop@95", "Assured, no stop")]
    fig, ax = plt.subplots(1, 3, figsize=(COLW, 1.45))
    for a, (metric, lab) in zip(ax, [("intervention_rate", "(a) Interventions"), ("fallback_success", "(b) Fallback success"),
                                     ("safe_stop_rate", "(c) Safe stops")]):
        grouped(a, d, ms, metric, "", small=True)
        a.set_title(lab, fontsize=7)
    h, l = ax[0].get_legend_handles_labels()
    fig.legend(h, l, ncol=4, loc="upper center", bbox_to_anchor=(0.5, 1.1), frameon=False, fontsize=5.8, handlelength=1.0, columnspacing=0.7)
    fig.tight_layout(w_pad=0.5)
    save(fig, "fig5_interventions")


def fig6(d):
    abl = [("ens", "Ensemble only"), ("assured-ood_only@95", "OOD only"), ("assured-unc_only@95", "Unc. only"),
           ("assured-monitor_only@95", "Rules only"), ("assured-no_ood@95", "Full − OOD"), ("assured-no_unc@95", "Full − unc."),
           ("assured-no_monitor@95", "Full − rules"), ("assured@95", "Full")]
    fig, ax = plt.subplots(1, 2, figsize=(COLW, 1.95), sharey=True)
    for a, metric, lab in ((ax[0], "success", "Success rate"), (ax[1], "unsafe", "Unsafe / episode (log)")):
        y = np.arange(len(abl))
        for j, c in enumerate(CONDS):
            s_ = [stat(d, c, m, metric) for m, _ in abl]
            a.errorbar([v[0] for v in s_], y + (j - 2) * 0.13, xerr=[[v[1] for v in s_], [v[2] for v in s_]], fmt="o", ms=1.8,
                       lw=0.5, label=CLAB[c], color=["#000", "#E69F00", "#56B4E9", "#009E73", "#D55E00"][j])
        a.set_xlabel(lab, fontsize=6.5); a.grid(axis="x", lw=0.3, alpha=0.5); a.tick_params(labelsize=6)
        if metric == "unsafe":
            a.set_xscale("log")
    ax[0].set_yticks(np.arange(len(abl)), [l for _, l in abl], fontsize=6)
    h, l = ax[0].get_legend_handles_labels()
    fig.legend(h, l, ncol=5, loc="upper center", bbox_to_anchor=(0.55, 1.06), frameon=False, fontsize=5.8, handlelength=1.0, columnspacing=0.6)
    fig.tight_layout(w_pad=0.6)
    save(fig, "fig6_ablation")


def fig7(d):
    fig, ax = plt.subplots(1, 3, figsize=(COLW, 1.4))
    for a, (metric, lab) in zip(ax, [("success", "(a) Success"), ("unsafe", "(b) Unsafe / ep."), ("intervention_rate", "(c) Interventions")]):
        for j, c in enumerate(CONDS):
            s_ = [stat(d, c, f"assured@{p}", metric) for p in (90, 95, 99)]
            a.errorbar([90, 95, 99], [v[0] for v in s_], yerr=[[v[1] for v in s_], [v[2] for v in s_]], marker="o", ms=2, lw=0.7,
                       capsize=1.2, label=CLAB[c], color=["#000", "#E69F00", "#56B4E9", "#009E73", "#D55E00"][j])
        a.set_xticks([90, 95, 99]); a.set_title(lab, fontsize=7); a.grid(lw=0.3, alpha=0.5); a.tick_params(labelsize=6)
    ax[1].set_xlabel("Threshold percentile", fontsize=6.5)
    h, l = ax[0].get_legend_handles_labels()
    fig.legend(h, l, ncol=5, loc="upper center", bbox_to_anchor=(0.5, 1.1), frameon=False, fontsize=5.8, handlelength=1.0, columnspacing=0.6)
    fig.tight_layout(w_pad=0.5)
    save(fig, "fig7_sensitivity")


def fig8():
    p = H3 / "analysis/final/h3_paired.csv"
    if not p.exists():
        print("  (no amendment-A1 analysis yet: skipping fig8_h3)")
        return
    rows = list(csv.DictReader(open(p)))
    want = [("energy_feasible_intervention_rate", "(a) Δ no-depletion"), ("success", "(b) Δ success"), ("energy_used", "(c) Δ energy")]
    fig, ax = plt.subplots(1, 3, figsize=(COLW, 1.25))
    comps = sorted({r["comparison"] for r in rows})
    for a, (metric, lab) in zip(ax, want):
        for k, comp in enumerate(comps):
            rr = [next(r for r in rows if r["comparison"] == comp and r["metric"] == metric and r["condition"] == c) for c in CONDS]
            x = np.arange(len(CONDS)) + (k - 0.5) * 0.3
            m = np.array([float(r["diff"]) for r in rr])
            lo, hi = np.array([float(r["lo"]) for r in rr]), np.array([float(r["hi"]) for r in rr])
            a.errorbar(x, m, yerr=[m - lo, hi - m], fmt="o" if k == 0 else "s", ms=2.3, lw=0.7, capsize=1.2,
                       color=["black", "#888888"][k], label="with safe stop" if "no stop" not in comp else "without safe stop")
        a.axhline(0, lw=0.5, color="#555"); a.set_xticks(range(len(CONDS)), [CLAB[c] for c in CONDS], rotation=40, fontsize=5.5)
        a.set_title(lab, fontsize=7); a.grid(axis="y", lw=0.3, alpha=0.5); a.tick_params(axis="y", labelsize=6)
    h, l = ax[0].get_legend_handles_labels()
    fig.legend(h, l, ncol=2, loc="upper center", bbox_to_anchor=(0.5, 1.1), frameon=False, fontsize=6)
    fig.tight_layout(w_pad=0.4)
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
    fig, ax = plt.subplots(1, 2, figsize=(COLW, 1.3))
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
    sites = [("victoria", "Victoria (Opportunity)"), ("jezero", "Jezero (Perseverance)"), ("gale", "Gale (Curiosity)")]
    fig = plt.figure(figsize=(COLW, 2.15))
    gs = fig.add_gridspec(2, 3, height_ratios=[1.25, 0.75], hspace=0.45, wspace=0.08)
    for j, (site, lab) in enumerate(sites):
        a = fig.add_subplot(gs[0, j])
        i = next(k for k in range(len(z["seeds"])) if z["site"][k] == site and z["split"][k] == "real_final")
        a.imshow(z["grids"][i], cmap=ListedColormap(TERRAIN_COLORS), vmin=0, vmax=3, interpolation="nearest")
        a.set_title(lab, fontsize=6.5); a.set_xticks([]); a.set_yticks([])
        for sp in a.spines.values():
            sp.set_visible(False)
    a = fig.add_subplot(gs[1, :])
    names = ["normal", "sand", "rock", "obstacle"]
    labels = ["Victoria", "Jezero", "Gale", "Procedural ID"]
    comps = [[meta["sites"][s_]["composition"][k] for k in names] for s_, _ in sites] + [[0.60, 0.15, 0.10, 0.15]]
    left = np.zeros(4)
    for j, k in enumerate(names):
        v = np.array([c[j] for c in comps])
        a.barh(np.arange(4), v, left=left, color=TERRAIN_COLORS[j], edgecolor="#333", lw=0.3, label=k); left += v
    a.set_yticks(np.arange(4), labels, fontsize=6); a.invert_yaxis(); a.set_xlim(0, 1); a.tick_params(axis="x", labelsize=6)
    a.set_xlabel("Fraction of cells", fontsize=6.5)
    a.legend(fontsize=5.8, frameon=False, ncol=4, loc="lower center", bbox_to_anchor=(0.45, 1.0), handlelength=1.0, columnspacing=0.8)
    save(fig, "fig10_real_tiles")


def fig11():
    """Real-terrain tiles under nominal and shifted physics (amendments A2, A4)."""
    from src.evaluation.metrics import episode_metrics, load_run
    a2 = ROOT / "results/phase2/a2"; a4 = ROOT / "results/phase2/a4"
    if not (a2.exists() and a4.exists()):
        print("  (no A2/A4 runs: skipping fig11_real_shift)")
        return
    runs = {"real_hirise": load_run(a2, "real_final")["real_hirise"]}
    r4 = load_run(a4, "real_final")
    runs.update({k: r4[k] for k in ("real_sensor", "real_dynamics", "real_combined")})
    conds = [("real_hirise", "ID"), ("real_sensor", "Sensor"), ("real_dynamics", "Dynamics"), ("real_combined", "Combined")]
    ms = [("astar", "A*"), ("astar_monitor", "A*+monitor"), ("dqn_shield", "DQN+shield"), ("ens", "Ensemble"),
          ("assured@95", "Assured"), ("assured-aood@95", "Assured, act.-OOD")]
    col = dict(COL); col["assured-aood@95"] = "#332288"
    fig, ax = plt.subplots(1, 2, figsize=(COLW, 1.45))
    for a, metric, lab, log in ((ax[0], "success", "(a) Success", False), (ax[1], "unsafe", "(b) Unsafe / episode (log)", True)):
        n = len(ms); w = 0.8 / n; x = np.arange(len(conds))
        for i, (m, ml) in enumerate(ms):
            vals, err = [], []
            for c, _ in conds:
                v = [episode_metrics(rows)[metric] for rows in runs[c][m].values()]
                ci = mean_ci(v) if len(v) > 1 else {"mean": v[0], "lo": v[0], "hi": v[0]}
                vals.append(ci["mean"]); err.append(ci["hi"] - ci["mean"] if len(v) > 1 else 0)
            a.bar(x + (i - (n - 1) / 2) * w, vals, w, yerr=err, color=col[m], label=ml, error_kw={"lw": 0.5, "capsize": 1},
                  edgecolor="white", linewidth=0.3)
        a.set_xticks(x, [l for _, l in conds], fontsize=5.5, rotation=25); a.set_title(lab, fontsize=7); a.tick_params(axis="y", labelsize=6)
        a.grid(axis="y", lw=0.3, alpha=0.5)
        if log:
            a.set_yscale("log")
        else:
            a.set_ylim(0.9, 1.0)
    h, l = ax[0].get_legend_handles_labels()
    fig.legend(h, l, ncol=3, loc="upper center", bbox_to_anchor=(0.5, 1.17), frameon=False, fontsize=6, handlelength=1.0, columnspacing=0.8)
    fig.tight_layout(w_pad=0.8)
    save(fig, "fig11_real_shift")


def fig12():
    """Trajectories of A* and the assured system on one real-terrain PILOT tile under combined-shift physics (illustration only)."""
    from matplotlib.colors import ListedColormap
    from src.config import load_config
    from src.evaluation.evaluator import make_env
    from src.evaluation.experiment import build_method
    from src.evaluation.replay import TERRAIN_COLORS, record_episode
    from src.evaluation.reproducibility import SPLIT_OFFSET
    cfg = load_config(ROOT / "configs/sim32_real_combined.yaml")
    env, ev = make_env(cfg.env, 0)

    from src.assurance.layout import STOP_ACTION

    def run(spec, seed):
        """Minimal recorder (handles the safe-stop action like the evaluation harness does)."""
        pol = build_method(spec, 0, ROOT, keep_log=spec.startswith("assured"))
        pol.attach(env.explored_map, env.max_battery)
        obs = env.reset(seed=seed)
        rec = {"grid": ev.grid.tolist(), "initial": {"pos": list(env.position)}, "steps": []}
        done, info = False, {}
        while not done:
            act = int(pol.act(obs)); before = env.position
            obs, _, done, info = env.safe_stop() if act == STOP_ACTION else env.step(act)
            rec["steps"].append({"from": list(before), "to": list(env.position), "event": info["event"]})
        rec["success"] = int(info["reason"] == "goal")
        return rec, getattr(pol, "log", [])

    best = None
    for seed in range(SPLIT_OFFSET["real_pilot"], SPLIT_OFFSET["real_pilot"] + 60):
        ra, _ = run("astar", seed); rb, lb = run("assured-aood@95", seed)
        ca = sum("collision" in s_["event"] for s_ in ra["steps"]); cb = sum("collision" in s_["event"] for s_ in rb["steps"])
        if ra["success"] and rb["success"] and (best is None or ca - cb > best[0]):
            best = (ca - cb, seed, ra, rb, lb)
    _, seed, ra, rb, lb = best
    fig, ax = plt.subplots(1, 2, figsize=(COLW, 1.65))
    for a, rec, lab, log in ((ax[0], ra, "(a) A*", []), (ax[1], rb, "(b) Assured, act.-OOD", lb)):
        a.imshow(np.array(rec["grid"]), cmap=ListedColormap(TERRAIN_COLORS), vmin=0, vmax=3, interpolation="nearest")
        path = [tuple(rec["initial"]["pos"])] + [tuple(s_["to"]) for s_ in rec["steps"]]
        a.plot([p_[1] for p_ in path], [p_[0] for p_ in path], "-", c="#0072B2", lw=1.1)
        for s_ in rec["steps"]:
            if "collision" in s_["event"]:
                a.plot(s_["from"][1], s_["from"][0], "o", mfc="none", mec="#D55E00", ms=4, mew=1.0)
        for d_, s_ in zip(log, rec["steps"]):
            if d_["source"] == "fallback":
                a.plot(s_["from"][1], s_["from"][0], "x", c="black", ms=3, mew=0.8)
        nc = sum("collision" in s_["event"] for s_ in rec["steps"])
        a.set_title(f"{lab}: {nc} collisions", fontsize=6.5)
        a.set_xticks([]); a.set_yticks([])
        for sp in a.spines.values():
            sp.set_visible(False)
    fig.tight_layout(w_pad=0.5)
    print("  fig12 tile seed", seed)
    save(fig, "fig12_trajectories")


if __name__ == "__main__":
    d = load_by_seed(MAIN)
    fig1(); fig2(); fig3(d); fig4(d); fig5(d); fig6(d); fig7(d); fig8(); fig9(); fig10(); fig11(); fig12()
