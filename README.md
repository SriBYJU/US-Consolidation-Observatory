# U.S. Consolidation Observatory

**Open empirical research on business structure, dynamism, and future consolidation signals.**

The Observatory is designed around a simple standard: **data and falsifiable evaluation before marketing claims**. The current public research preview uses the U.S. Census Bureau's 2023 Business Dynamics Statistics (BDS) State × Sector file to construct a 44,574-row longitudinal panel covering 51 jurisdictions, 19 NAICS sectors, and 1978–2023.

## What is live in v0.2

- Interactive state × sector explorer with 2014–2023 browser data.
- Full 1978–2023 cleaned research panel is deterministically rebuilt in CI from the official Census BDS source; generated artifacts are deployed to GitHub Pages rather than committed as opaque binaries.
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
- Public source registry and SHA-256 provenance manifest.
- Local evidence-query tool that never invents data.
- Forecast-ledger protocol that blocks M&A forecasting claims until transaction outcomes are verified.
- Research methodology, limitations, transaction schema, AI benchmark protocol, and release checklist.

## What v0.2 **does not claim**

The current model target is **two-year-ahead establishment growth**, not M&A activity. The flagship transaction-level research report is intentionally still a future milestone rather than being simulated with invented deal data. BDS does not contain transaction-level acquisition outcomes. Therefore this release does not claim that its exploratory score predicts acquisitions, valuations, investment returns, or private-equity performance. See [`RESEARCH_MILESTONES.md`](RESEARCH_MILESTONES.md) for the empirical work required before such a claim could be tested.

## Reproduce

```bash
python -m pip install -r requirements.txt
BDS_SOURCE=/path/to/bds2023_st_sec.csv python scripts/build_research_assets.py
python scripts/run_score_sensitivity.py
python scripts/build_advanced_diagnostics.py
node --check assets/app-core.js
node --check assets/app.js
python scripts/validate_release.py
python -m http.server 8000
```

Open `http://localhost:8000`.

The exact official source URL and expected source-file SHA-256 are documented in the build pipeline. CI verifies the downloaded Census file before generating derived artifacts.

## Repository structure

```text
assets/                 Static app CSS + JavaScript
data/                   Small schemas/manifests tracked in Git; large derived artifacts are CI-generated
research/               Methods, protocols, limits, paper/report drafts
scripts/                Deterministic data build, modeling, and release validation
.github/workflows/       Automated release-gate checks
MASTER_CHECKLIST.md      Build/QA gates that must pass before push/release
RESEARCH_MILESTONES.md   Real-world research milestones that cannot be fabricated
```

## Core design principle

The project deliberately separates:

1. **Structural descriptors** — what public business-dynamics data can support today.
2. **Predictive evaluation** — what a locked, point-in-time holdout actually shows.
3. **M&A outcomes** — a future verified transaction corpus, not inferred from BDS.
4. **Impact/adoption** — evidence that must come from real external users and reviewers.

## Official data sources

Primary data: U.S. Census Bureau, Business Dynamics Statistics (BDS), 2023 State × Sector CSV.

Context / planned enrichment: BLS QCEW, Census CBP, BEA GDP by State, Census Nonemployer Statistics, SEC EDGAR.

## License

Code is released under the MIT License. U.S. federal statistical data remain subject to their issuing agencies' terms and disclosure rules. Source attribution is retained throughout the project.
