# U.S. Consolidation Observatory

**Open empirical research on business structure, dynamism, and future consolidation signals.**

The Observatory is designed around a simple standard: **data and falsifiable evaluation before marketing claims**. The core research panel uses the U.S. Census Bureau's 2023 Business Dynamics Statistics (BDS) State × Sector file to construct a 44,574-row longitudinal panel covering 51 jurisdictions, 19 NAICS sectors, and 1978–2023.

Version 0.4 adds a separate **current-context layer** so the platform can stay useful in the present without contaminating the historical point-in-time research design. Current context now includes BLS QCEW through Q4 2025, Census Business Formation Statistics through July 2026, and BEA GDP by State through Q1 2026. These newer sources are clearly labeled as context and do **not** change the current Structural Readiness Score.

## What is live in v0.4

- Interactive state × sector explorer with 2014–2023 browser data.
- Full 1978–2023 cleaned research panel deterministically rebuilt from the official Census BDS source.
- Transparent exploratory Structural Readiness Score with component decomposition.
- Point-in-time model lab with train/validation/holdout separation.
- Persistence, Ridge, and Histogram Gradient Boosting comparisons.
- Holdout failure analysis by sector.
- Four-window rolling-origin robustness backtest using the fixed HGB specification.
- Historical SRS replay with realized two-year establishment-growth outcomes.
- 1,000-run score-weight robustness intervals surfaced per 2023 market.
- Validation-period permutation importance and leave-one-feature-out diagnostics.
- Three-market comparator, transparent evidence screener, and source-attributed market-brief export.
- Model card, falsifiable claims/hypothesis registry, and machine-readable reproducibility fingerprint.
- **Current Context layer** with a freshness matrix and dated federal releases.
- **Census BFS July 2026** business-formation pulse.
- **BLS QCEW Q4 2025** employment and wage pulse.
- **BEA Q1 2026** state GDP context.
- **Census CBP** and **SEC EDGAR** registered as evidence/enrichment sources with explicit roles.
- Machine-readable current-source registry in `data/current_context.json`.
- Source-governance and mixed-vintage policy in `research/source-governance.md`.
- Local evidence-query tool that never invents data.
- Forecast-ledger protocol that blocks M&A forecasting claims until transaction outcomes are verified.
- Research methodology, limitations, transaction schema, AI benchmark protocol, and release checklist.

## What v0.4 **does not claim**

The current validated model target is **two-year-ahead establishment growth**, not M&A activity. The flagship transaction-level research report is intentionally still a future milestone rather than being simulated with invented deal data. BDS does not contain transaction-level acquisition outcomes. Therefore this release does not claim that its exploratory score predicts acquisitions, valuations, investment returns, or private-equity performance.

Newer QCEW, BFS, and BEA statistics are shown as **current context only**. They are not silently mixed into a 2023 SRS. This preserves a clean point-in-time evidence chain.

See [`RESEARCH_MILESTONES.md`](RESEARCH_MILESTONES.md) for the empirical work required before direct M&A forecasting can be tested.

## Data architecture

The project deliberately separates two evidence layers:

1. **Historical research layer** — Census BDS State × Sector data used for SRS and current forecasting experiments.
2. **Current-context layer** — newer official federal releases used to interpret the present environment without introducing future information into historical scores.

The current-context registry records agency, product, latest vintage, release date, role, official URL, and whether each source is used in SRS.

## Reproduce

```bash
python -m pip install -r requirements.txt
BDS_SOURCE=/path/to/bds2023_st_sec.csv python scripts/build_research_assets.py
python scripts/run_score_sensitivity.py
python scripts/build_advanced_diagnostics.py
node --check assets/app-core.js
node --check assets/app-ui.js
node --check assets/app.js
python scripts/validate_release.py
python scripts/end_to_end_audit.py
python -m http.server 8000
```

Open `http://localhost:8000`.

The exact official source URL and expected source-file SHA-256 are documented in the build pipeline. CI verifies the downloaded Census file before generating derived research artifacts. Current-context source metadata are stored separately in `data/current_context.json`.

## Repository structure

```text
assets/                 Static app CSS + JavaScript
data/                   Research artifacts, manifests, and current-context registry
research/               Methods, source governance, protocols, limits, paper/report drafts
scripts/                Deterministic data build, modeling, and release validation
.github/workflows/       Automated release-gate checks
MASTER_CHECKLIST.md      Build/QA gates that must pass before push/release
RESEARCH_MILESTONES.md   Real-world research milestones that cannot be fabricated
```

## Core design principle

The project deliberately separates:

1. **Structural descriptors** — what public business-dynamics data can support.
2. **Current context** — fresher official indicators that describe the present without changing historical scores.
3. **Predictive evaluation** — what a locked, point-in-time holdout actually shows.
4. **M&A outcomes** — a future verified transaction corpus, not inferred from BDS.
5. **Impact/adoption** — evidence that must come from real external users and reviewers.

## Official data sources

**Core research source**
- U.S. Census Bureau — Business Dynamics Statistics (BDS), 2023 State × Sector release.

**Current context**
- U.S. Bureau of Labor Statistics — Quarterly Census of Employment and Wages (QCEW), Q4 2025 context.
- U.S. Census Bureau — Business Formation Statistics (BFS), July 2026 context.
- U.S. Bureau of Economic Analysis — GDP by State, Q1 2026 context.

**Registered enrichment / evidence sources**
- U.S. Census Bureau — County Business Patterns (CBP).
- U.S. Securities and Exchange Commission — EDGAR.

See [`research/source-governance.md`](research/source-governance.md) and [`data/current_context.json`](data/current_context.json) for freshness rules and exact official links.

## License

Code is released under the MIT License. U.S. federal statistical data remain subject to their issuing agencies' terms and disclosure rules. Source attribution is retained throughout the project.
