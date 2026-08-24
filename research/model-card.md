# Model Card — v0.2 Establishment-Growth Research Model

## Model purpose

The current model exists to test whether the Observatory's point-in-time research pipeline can extract signal about a **future observable business-dynamics outcome**. Its target is two-year-ahead annualized log establishment growth.

It is **not** an M&A prediction model, investment model, valuation model, or underwriting system.

## Data

Primary panel: U.S. Census Bureau Business Dynamics Statistics, State × Sector, 1978–2023.

Model features at year `t`:

- firms per 1,000 employees;
- establishment entry rate;
- establishment exit rate;
- net job-creation rate;
- reallocation rate;
- log firm count;
- log employment;
- trailing two-year annualized establishment growth.

Target: annualized log establishment growth from `t` to `t+2`.

## Frozen v0.1 evaluation design

- Training: 1990–2016
- Model-selection validation: 2017–2019
- Locked holdout feature years: 2020–2021
- Holdout outcomes: 2022–2023
- Selection rule: lowest validation MAE

The selected model was Histogram Gradient Boosting. The original holdout result remains reported even though Ridge had slightly lower holdout MAE; the model is not re-selected after observing the holdout.

## Locked holdout performance

| Model | MAE ↓ | Spearman ↑ | Top-decile precision ↑ |
|---|---:|---:|---:|
| Persistence | 2.110 | 0.391 | 28.9% |
| Ridge | **1.866** | 0.369 | 28.4% |
| Selected HGB | 1.887 | 0.380 | **33.5%** |

This is intentionally a mixed result. The selected HGB improves MAE and top-decile precision versus persistence but does not beat persistence on holdout rank correlation.

## Post-hoc robustness diagnostics

The fixed HGB specification was evaluated in four rolling-origin windows: 2010–2012, 2013–2015, 2016–2018, and 2019–2021. In each window the model was trained only on earlier observations.

The HGB model beat persistence in **4/4 windows** on each of MAE, Spearman rank correlation, and top-decile precision. This is a robustness diagnostic, not a replacement for the original locked holdout.

## Feature diagnostics

Permutation analysis on the 2017–2019 validation period indicates that establishment entry rate and trailing two-year establishment growth are the two strongest contributors to validation MAE. Leave-one-feature-out diagnostics also show that some inputs add little or may be redundant. These diagnostics are reported rather than used to rewrite the frozen v0.1 result.

## Intended use

Appropriate uses:

- research on public business-dynamics data;
- evaluation-methodology demonstrations;
- comparing forecasting approaches;
- generating hypotheses for later transaction-level study.

Inappropriate uses:

- recommending an acquisition;
- predicting deal returns;
- estimating enterprise value;
- assessing a company's management or cash flow;
- claiming a market will consolidate;
- making lending or investment decisions.

## Known limitations

- BDS does not identify acquisition events.
- State × broad-sector aggregation is coarse.
- The holdout includes pandemic-era dynamics and may represent unusual distribution shift.
- Public statistical releases are lagged.
- A model can predict establishment growth without predicting M&A activity.
- Feature diagnostics are post-selection and should not be confused with causal importance.

## Accountability

The public release keeps the M&A forecast ledger empty until a verified transaction corpus exists. Future forecasts must record data vintage and Git commit SHA and are append-only by protocol.
