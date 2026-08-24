# Release Audit — v0.2 Technical Platform

- Release-gate validator: **62/62 PASS**
- JavaScript syntax: **PASS** (`node --check`)
- Local HTTP smoke test: **PASS** for homepage, CSS, JS, replay, diagnostics, reproducibility manifest, and research docs
- JS-to-HTML control reference check: **PASS** — no missing referenced element IDs
- Official BDS source SHA-256: `ba73f1ad58749d57f04c6bb56b0618c92384897a3e9f793de0df7b23f1f1868a`
- Clean panel: **44,574** unique state-sector-year records, **1978–2023**, **51** jurisdictions, **19** sectors
- Locked holdout observations: **1,934**
- Selected model holdout MAE: **1.887** vs. persistence **2.110**
- Selected model holdout Spearman: **0.380** vs. persistence **0.391**
- Selected model holdout top-decile precision: **33.5%** vs. persistence **28.9%**
- Historical SRS replay: **43/44** annual cohorts show positive top-quintile future-establishment-growth uplift; mean uplift **+0.790** annualized log percentage points
- Rolling-origin robustness: fixed HGB beats persistence in **4/4** windows on MAE, Spearman, and top-decile precision
- Interactive replay artifact: **7,583** market-year observations for 2014–2021
- Score-weight robustness: **1,000** deterministic perturbations for the 2023 complete-score universe
- Reproducibility manifest: environment versions + SHA-256 fingerprints for core scripts, UI files, research documents, and derived artifacts

## v0.2 elevation completed

The technical platform now includes:

- three-market comparator;
- transparent threshold screener;
- source-attributed evidence-brief export;
- per-market score robustness interval and top-quintile stability probability;
- historical point-in-time replay with realized future outcomes;
- 44-cohort uplift visualization;
- rolling-origin robustness backtests;
- validation-period permutation importance;
- leave-one-feature-out diagnostics;
- model card;
- claims/hypothesis registry;
- reproducibility/evidence-lineage documentation;
- machine-readable release fingerprint;
- CI rebuild of advanced diagnostics before release validation.

## Integrity note

The current predictive outcome is two-year-ahead establishment growth, **not M&A activity**. The historical replay and rolling-origin diagnostics are additional establishment-growth evidence and are explicitly labeled exploratory/post-hoc where appropriate.

The verified M&A transaction corpus, human-labeled AI extraction benchmark, final flagship transaction-level research report, outside expert review, real practitioner adoption, and independent recognition remain real future milestones in `RESEARCH_MILESTONES.md`; they are not fabricated or marked complete.
