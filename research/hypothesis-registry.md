# Research Claims & Hypothesis Registry

This file makes the Observatory's claims falsifiable. It is a versioned internal research registry, **not a claim of external preregistration**.

## Current establishment-growth tests

### E1 — A multivariate point-in-time model can improve future-growth MAE versus persistence

**Test:** selected model vs. trailing-growth persistence on the locked 2020–2021 feature-year holdout.

**Result:** supported on MAE. Selected HGB MAE = 1.887 versus persistence = 2.110 annualized log-percentage points.

**Boundary:** this says nothing directly about acquisitions.

### E2 — The selected model can improve identification of the future top growth decile

**Test:** top-decile precision on the locked holdout.

**Result:** supported. Selected HGB = 33.5% versus persistence = 28.9%.

### E3 — The selected model should improve rank ordering versus persistence

**Test:** holdout Spearman correlation.

**Result:** not supported on the original locked holdout. HGB = 0.380 versus persistence = 0.391.

This negative result remains public.

### E4 — Performance should not depend on a single favorable historical window

**Test:** fixed-specification rolling-origin robustness windows, trained only on data available before each window.

**Result:** post-hoc support. HGB beats persistence in 4/4 tested windows on MAE, Spearman, and top-decile precision.

**Boundary:** this is retrospective robustness analysis and does not replace a truly future frozen forecast.

## Exploratory structural-score finding

### X1 — High-SRS markets tend to show stronger subsequent establishment growth

**Test:** within each year and sector, compare states in the SRS top quintile with the remaining states, then observe two-year-ahead annualized log establishment growth.

**Result:** exploratory/post-hoc. The top quintile outgrew the remainder in 43 of 44 annual cohorts from 1978–2021; mean annualized log-growth uplift was +0.790 percentage points.

**Important:** SRS was not optimized against this future-growth outcome. This is a descriptive empirical pattern, not causal evidence and not M&A validation.

## Future M&A hypotheses — not yet testable

### M1 — Public structural variables contain out-of-sample signal for subsequent acquisition activity

Status: **not tested**. Requires verified transaction corpus.

Minimum standard before testing:

- point-in-time event dates and source evidence;
- explicit coverage-bias analysis;
- train/validation/untouched holdout separation;
- simple acquisition-activity baselines;
- sector/geography error analysis.

### M2 — A multivariate model adds signal beyond historical acquisition activity alone

Status: **not tested**.

### M3 — Structural fragmentation is useful only in interaction with target density or business dynamism

Status: **not tested**. This is a candidate interaction hypothesis, not a conclusion.

## Rule for future versions

A failed hypothesis is not deleted. It is marked unsupported, the evidence is retained, and any replacement hypothesis receives a new identifier/version.
