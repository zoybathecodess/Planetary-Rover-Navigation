# Targeted literature review (plan §1.5 / §7 novelty check)

Done 2026-11-24 with web searches over arXiv, AAAI, NeurIPS, IEEE, MDPI and CVF. BibTeX is in `paper/references.bib`.
This is a **targeted** check of the closest work, not a systematic review. Before submission, add a database search
(IEEE Xplore, Scopus) for 2025–2026 and check every entry marked VERIFY in the .bib.

## 1. Closest prior work, by component

| Strand | Representative work | What they do | How MAREC differs |
|---|---|---|---|
| Simplex / runtime assurance | Sha 2001; Hobbs et al. 2023 (tutorial); Phan et al. 2020 (Neural Simplex); Mehmood et al. 2022 (Black-Box Simplex) | Unverified controller + verified/simple baseline + switching logic; triggers are mostly *safety conditions* | MAREC's triggers mix a rule monitor with *learned-confidence* signals (ensemble disagreement, OOD), and the fallback is a planner that must also respect an **energy budget** |
| Shielding for RL | Alshiekh et al. 2018; Carr et al. 2023 (shielding under partial observability) | Shields synthesised from a (partial) model; formal reach-avoid guarantees | MAREC's monitor is a hand-specified, *empirical* rule set (no formal guarantee claimed); we compare against such a rule shield as a baseline |
| Uncertainty / OOD-triggered fallback | Kahn et al. 2017; Lütjens et al. 2019; Sinha et al. 2023 (fallback-safe MPC); Stutts et al. 2024 (SODA-MPC, conformalised ensembles); evaluation-time policy switching (arXiv 2503.12222) | Ensemble or monitor uncertainty used to slow down, switch to a fallback, or adapt | Not rover-specific and do not study energy feasibility. SODA-MPC notes that raw ensemble disagreement is **uncalibrated**, which matches what we find |
| Planetary rover navigation | Toupet et al. 2020 (ENav); Swan et al. 2021 (AI4Mars); Endo et al. 2024 (probabilistic traversability + test-time adaptation); Mortensen et al. 2023 (teacher–student RL); Sensors 2024 lunar DQN with resource constraints; Remote Sensing 2025 review | Classical or learned traversability and planning; uncertainty-aware costs; RL navigation in simulation | None of them puts a **runtime-assurance layer** around a learned policy, or measures intervention, safe-stop and energy trade-offs under controlled shifts |
| Uncertainty under shift | Ovadia et al. 2019; Lakshminarayanan et al. 2017; Osband et al. 2018; Lee et al. 2018 | Ensembles / randomised priors / Mahalanobis OOD | Used as components, not claimed as contributions |

## 2. Gap statement (what may be claimed)

We found **no** work that, for a planetary rover under partial observability, combines (i) a learned policy with ensemble
disagreement, (ii) an OOD gate, (iii) an explicit onboard rule monitor, (iv) an energy-feasibility-aware fallback planner
and (v) safe stop, and evaluates the parts by ablation under controlled terrain, sensor and dynamics shifts with
pre-registered statistics. The component ideas are all established.

**Claimable contribution (precise):** an *information-constrained, pre-registered empirical study* of runtime
assurance for a learned rover navigator. It includes the component-level finding of *which* assurance signals actually
help under which shift (the rule monitor does; ensemble disagreement helps a little; raw Mahalanobis OOD over-fires under
sensor shift), a pre-registered repair of that failure (amendment A3: an action-conditioned feature-space gate removes the
harm but adds no value over no OOD gate), and the role of energy-aware fallback (H3, amendment A1: decisive under combined shift).

**Not claimable:** first-of-its-kind architecture; formal safety; calibrated failure probabilities; real-rover performance.

## 3. Reviewer risks to answer in the paper
1. "A* + monitor gets the same success: why learn at all?" The paper must report this openly (it's in Table III). The
   learned proposer's measurable benefit is fewer attempted unsafe moves and slightly less energy, not success.
2. "OOD gating is badly tuned." The threshold was fixed a priori at the ID-validation 95th percentile; the
   sensitivity analysis (90/95/99) shows the over-firing is not a threshold artefact under sensor shift.
3. "Procedural maps only." Answered partly by the planned real-terrain extension (docs/REAL_TERRAIN_EXTENSION.md).
