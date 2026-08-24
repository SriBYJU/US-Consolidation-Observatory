# Research Preview: Evaluating Public Structural Signals Before M&A Validation
## A Point-in-Time Framework for U.S. Business Dynamics

**U.S. Consolidation Observatory — Technical Research Preview v0.2**

### Abstract

This technical research preview constructs a 44,574-observation state-sector-year panel from the U.S. Census Bureau's 2023 Business Dynamics Statistics and develops a reproducible point-in-time evaluation framework for studying structural market signals. Because BDS does not contain acquisition events, v0.1 deliberately tests the framework on a narrower observable outcome: two-year-ahead establishment growth. Three models — a persistence baseline, Ridge regression, and Histogram Gradient Boosting — are trained on 1990–2016, selected using 2017–2019 validation data, and evaluated on a locked 2020–2021 feature-year holdout with 2022–2023 outcomes. Histogram Gradient Boosting is selected by validation MAE. On the holdout, it achieves MAE 1.887 annualized log-percentage points versus 2.110 for persistence, Spearman rank correlation 0.380, and top-decile precision 33.5% versus 28.9% for persistence. These results support the usefulness of the point-in-time research pipeline while also showing substantial prediction error and do **not** validate M&A forecasting. A post-hoc robustness layer additionally replays the Structural Readiness Score across historical cohorts and evaluates the fixed nonlinear specification across four rolling-origin windows. The next research stage still requires a human-verified acquisition-event corpus and coverage-bias analysis before consolidation predictions can be evaluated. This preview is not the final flagship M&A report.

## 1. Research motivation

Industry screening often combines market size, fragmentation, entry/exit, labor conditions, and regional momentum. The research question is whether a transparent public-data system can convert those structural descriptors into predictions that survive genuine out-of-sample testing.

The ultimate question is acquisition/consolidation activity, but a credible study cannot treat a non-transaction dataset as if it were a transaction database. Therefore the project separates **infrastructure validation** from **M&A outcome validation**.

## 2. Data

Primary input is the Census BDS State × Sector 2023 release. The panel spans 1978–2023, 51 jurisdictions, and 19 sectors. The source checksum is committed in `data/source_manifest.json`. Non-numeric suppression values remain missing.

## 3. Exploratory structural measure

The Structural Readiness Score combines within-sector-year percentiles for a fragmentation proxy, entry rate, net job creation, firm count, establishment stability, and reallocation. It is provided for transparent exploration, not as a validated investment score. Weight sensitivity is assessed with 1,000 deterministic perturbations.

## 4. Prediction design

The point-in-time target is two-year-ahead annualized log establishment growth. Features use only information available at year t. Models are trained on 1990–2016, selected on 2017–2019, and tested on a holdout with 2020–2021 feature years.

## 5. Results

| Model | Holdout MAE | Holdout Spearman | Holdout top-decile precision |
|---|---:|---:|---:|
| Persistence baseline | 2.110 | 0.391 | 28.9% |
| Ridge | **1.866** | 0.369 | 28.4% |
| Histogram Gradient Boosting* | 1.887 | 0.380 | **33.5%** |

\*Selected before seeing holdout results because it had the lowest validation MAE (1.388 vs. Ridge 1.456 and persistence 1.828).

This illustrates why a locked holdout matters: the validation winner did not dominate every holdout metric. The study reports that rather than swapping models after seeing the test set.

## 6. Advanced robustness diagnostics

The v0.2 technical platform adds three diagnostics that are deliberately separated from the original locked model-selection result.

**Historical SRS replay.** Across 44 annual cohorts from 1978–2021, states in the within-sector SRS top quintile had higher subsequent two-year annualized log establishment growth than the remaining states in 43 cohorts. Mean uplift was +0.790 percentage points. This is exploratory and post-hoc: SRS was not optimized against this future-growth outcome.

**Rolling-origin robustness.** The already-fixed Histogram Gradient Boosting specification was retrained using only observations available before four historical windows: 2010–2012, 2013–2015, 2016–2018, and 2019–2021. It beat persistence in all four windows on MAE, Spearman rank correlation, and top-decile precision. This does not replace the original locked holdout and is not M&A validation.

**Feature diagnostics.** Validation-period permutation analysis identifies establishment entry rate and trailing two-year establishment growth as the two strongest contributors to MAE performance. Leave-one-feature-out diagnostics are also published, including cases where removing an input slightly improves validation error. The project does not suppress those weak or redundant signals.

## 7. Error analysis

The selected model's largest sector-level holdout MAE occurs in mining/oil & gas, agriculture, utilities, arts/entertainment, and management of companies. These sectors may contain structural or cyclical behavior that a broad state-sector model captures poorly.

## 8. Interpretation

The evidence supports a modest conclusion: public business-dynamics features contain information useful for forecasting future establishment growth beyond a simple persistence baseline on some metrics. Rank performance remains modest and errors are material. Nothing in this result establishes acquisition causality or expected investment performance.

## 9. Next empirical stage

The M&A study requires:

- a verified public acquisition-event corpus;
- date-accurate source provenance;
- a human-labeled AI extraction benchmark;
- publication/coverage-bias analysis;
- point-in-time M&A outcomes and simple baselines;
- an untouched holdout;
- sensitivity, ablations, and failure analysis;
- a frozen public forecast ledger.

## 9. Reproducibility

All v0.1 transformations and model results are generated from scripts in `/scripts`. The browser app reads only generated, versioned artifacts from `/data`.

## 10. Limitations

See `research/limitations.md`. The most important limitation is that v0.1 does not contain transaction-level M&A outcomes and therefore does not claim to forecast them.
