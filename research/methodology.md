# Methodology

## Research question

The long-run research question is whether observable public information about industry structure and regional business dynamics can identify markets that later experience unusually strong consolidation/acquisition activity.

**Version 0.1 does not test that full claim.** The current release establishes the data and evaluation infrastructure using a narrower outcome that is directly observable in the Census BDS: two-year-ahead establishment growth.

## 1. Primary panel

Primary source: **U.S. Census Bureau, 2023 Business Dynamics Statistics — State by Sector**.

- Years: 1978–2023
- Jurisdictions: 50 states + District of Columbia
- NAICS sectors: 19
- Unique state-sector-year observations: 44,574
- Key: `(year, state FIPS, sector)`
- Duplicate keys in release build: 0

The exact source URL, SHA-256 digest, byte count, and coverage checks are saved in `data/source_manifest.json`.

### Disclosure/suppression handling

BDS may publish non-numeric disclosure/suppression values. The build converts these to missing values with `pandas.to_numeric(..., errors="coerce")`. Suppressed values are never interpreted as zero.

## 2. Exploratory Structural Readiness Score (SRS)

SRS is a descriptive comparison tool, **not a validated M&A forecast**.

For each year and sector independently, the platform calculates percentile ranks across states for:

1. **Fragmentation proxy (25%)** — firms per 1,000 employees. Higher values indicate more firms relative to sector employment. This is not HHI and does not measure revenue concentration.
2. **Establishment entry (20%)** — BDS establishment-entry rate.
3. **Net job-creation momentum (20%)** — BDS net job-creation rate.
4. **Firm scale (15%)** — percentile of firm count, used as a coarse target-density/market-size proxy.
5. **Establishment stability (10%)** — inverse percentile of establishment-exit rate.
6. **Dynamism (10%)** — percentile of BDS reallocation rate.

The declared score is:

`SRS = .25F + .20E + .20M + .15S + .10T + .10D`

A score is withheld if any of the six required components is missing.

### Sensitivity analysis

`run_score_sensitivity.py` generates 1,000 positive weight perturbations around the declared weights using deterministic random seed 42. For each 2023 state-sector record, the release stores the 5th, median, and 95th percentile score plus the probability the observation remains in its sector's top quintile. This does not validate economic causality; it tests whether rankings are fragile to moderate weighting changes.

## 3. Point-in-time validation framework

The current forecasting target is **two-year-ahead annualized log establishment growth**, defined from BDS establishment counts. It is intentionally a non-M&A target.

### Features at year t

- firms per 1,000 employees
- establishment entry rate
- establishment exit rate
- net job-creation rate
- reallocation rate
- log firm count
- log employment
- trailing two-year establishment growth

### Time split

- Training: 1990–2016
- Validation/model selection: 2017–2019
- Locked holdout feature years: 2020–2021
- Holdout outcomes: 2022–2023

The holdout is not used to select the model.

### Models

- Persistence baseline: trailing two-year establishment growth
- Ridge regression
- Histogram Gradient Boosting

Model selection is based only on validation MAE. The selected model in the generated release is Histogram Gradient Boosting.

### Metrics

- Mean absolute error (MAE) on annualized log-percentage-point growth
- Spearman rank correlation
- Top-decile precision: among observations in the predicted top decile, share actually in the realized top decile

The generated metrics are stored in `data/model_validation.json` and rendered verbatim by the app.

## 4. Failure analysis

The release reports the five sectors with the largest selected-model holdout MAE. This is included to make weak spots visible rather than hiding them.

## 5. Advanced diagnostics in v0.2

### Historical SRS replay

For every annual cohort with a two-year future establishment observation (1978–2021), SRS is ranked within year and sector. States in the top quintile are compared with the remaining states on subsequent two-year annualized log establishment growth. The resulting uplift series is exploratory and post-hoc; SRS weights were not optimized to this outcome.

### Rolling-origin robustness

The already-fixed HGB specification is trained on all eligible observations from 1990 through the year immediately before each test window. Four test windows are reported: 2010–2012, 2013–2015, 2016–2018, and 2019–2021. No rolling result is used to replace the original v0.1 locked holdout.

### Feature diagnostics

Permutation importance is computed on the 2017–2019 validation period using 20 deterministic repeats and MAE scoring. Leave-one-feature-out validation fits are also reported. These are model diagnostics rather than causal feature importance.

### Score sensitivity surfaced in the explorer

The previously generated 1,000-run score-weight perturbations are now rendered for each complete 2023 market as a 5th–95th percentile score interval and probability of remaining in the sector top quintile.

### Research claim governance

`research/hypothesis-registry.md` records supported, unsupported, exploratory, and not-yet-testable claims. `research/model-card.md` records intended and prohibited model uses. Unsupported claims are retained rather than deleted.

## 6. Future M&A outcome design

A transaction-level acquisition outcome will only be introduced after a verified event corpus exists. The event schema is in `research/transaction-schema.md` and `data/transaction_events_template.csv`.

The future model must preserve the same principles:

- point-in-time inputs only;
- date-stamped source evidence;
- separate train/validation/holdout periods;
- simple baselines;
- leakage checks;
- coverage-bias analysis;
- uncertainty and failure reporting;
- a frozen public forecast ledger before future outcomes are known.

## 7. Reproducibility

Run:

```bash
BDS_SOURCE=/path/to/bds2023_st_sec.csv python scripts/build_research_assets.py
python scripts/run_score_sensitivity.py
python scripts/build_advanced_diagnostics.py
python scripts/validate_release.py
```

All generated claims on the public site either come from versioned data artifacts in `/data` or from official agency sources listed in the source registry.
