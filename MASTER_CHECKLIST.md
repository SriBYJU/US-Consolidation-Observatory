# Master Release Checklist — v0.2

**Rule:** every item in this file is a push/release gate. Items requiring future human data collection, external reviewers, professional adoption, or external recognition live separately in `RESEARCH_MILESTONES.md` so the project never pretends they already happened.

## A. Identity and repository

- [x] Final research name locked: **U.S. Consolidation Observatory**.
- [x] Recommended repository name locked: **`US-Consolidation-Observatory`**.
- [x] Research framing is empirical and non-promotional rather than “AI replaces Bloomberg/PitchBook.”
- [x] README explains what is live and what is not yet supported.
- [x] MIT code license included.
- [x] GitHub Pages-compatible static architecture implemented.

## B. Credible public-data foundation

- [x] Official Census BDS **State × Sector** file used — not the incorrect metro-status cross-tab.
- [x] Exact official source URL recorded.
- [x] Source SHA-256 digest recorded for provenance.
- [x] Raw-source byte count recorded.
- [x] 44,574 state-sector-year records validated.
- [x] 1978–2023 coverage validated.
- [x] 51 jurisdictions validated (50 states + D.C.).
- [x] 19 NAICS-sector coverage validated.
- [x] Duplicate `(year, state, sector)` keys tested and confirmed absent.
- [x] Census suppression/non-numeric codes converted to missing values, never zero.
- [x] Full cleaned panel published as a compressed derived data artifact.
- [x] Browser-optimized 2014–2023 panel generated.
- [x] 2023 cross-section generated for ranking/search.
- [x] Data dictionary documents direct and derived variables.

## C. Public-data context and source validation

- [x] BDS primary-source description linked to U.S. Census Bureau.
- [x] BLS QCEW official 2024 context data shown with source link.
- [x] BEA GDP-by-State official source registered.
- [x] Census County Business Patterns official source registered for planned enrichment.
- [x] Census Nonemployer Statistics official source registered for planned enrichment.
- [x] SEC EDGAR official source registered for future transaction-corpus evidence.
- [x] Public-data claims are visually separated from research-derived model claims.

## D. Structural research layer

- [x] Exploratory **Structural Readiness Score (SRS)** implemented.
- [x] SRS explicitly labeled descriptive/exploratory rather than validated M&A forecasting.
- [x] Fragmentation proxy documented as firms per 1,000 employees.
- [x] Fragmentation proxy explicitly distinguished from HHI/market-share concentration.
- [x] Establishment entry component implemented.
- [x] Net job-creation momentum component implemented.
- [x] Firm-scale component implemented.
- [x] Establishment-stability component implemented.
- [x] Reallocation/dynamism component implemented.
- [x] Percentile comparison is within the same sector and year.
- [x] Score is withheld when a required component is missing.
- [x] Score data-completeness field is generated.
- [x] Exact score weights are disclosed on the site and in methodology.

## E. Robustness / sensitivity

- [x] Deterministic score-sensitivity script implemented.
- [x] 1,000 plausible positive weight perturbations generated.
- [x] 5th / median / 95th percentile score range generated for 2023 observations.
- [x] Top-quintile ranking stability probability generated.
- [x] Sensitivity is described as robustness-to-weights, not causal validation.

## F. Point-in-time forecasting architecture

- [x] Forecast target defined using a genuinely future observable outcome.
- [x] v0.1 target explicitly named: two-year-ahead establishment growth.
- [x] v0.1 target explicitly distinguished from acquisition/M&A activity.
- [x] Lagged growth baseline implemented.
- [x] Ridge regression implemented.
- [x] Histogram Gradient Boosting implemented.
- [x] Train period frozen at 1990–2016.
- [x] Model-selection validation period frozen at 2017–2019.
- [x] Holdout feature years frozen at 2020–2021 with 2022–2023 outcomes.
- [x] Holdout excluded from model selection.
- [x] MAE reported.
- [x] Spearman rank correlation reported.
- [x] Top-decile precision reported.
- [x] Model-selection rule documented.
- [x] Selected model beats persistence baseline on holdout MAE in generated release.
- [x] Mixed results are shown rather than cherry-picking a different model after holdout inspection.
- [x] Sector-level failure analysis generated.
- [x] Pandemic-era holdout limitation disclosed.

## G. M&A outcome integrity

- [x] BDS is explicitly described as **not** an M&A database.
- [x] No transaction count, transaction accuracy, or acquisition-prediction statistic is fabricated.
- [x] Verified transaction-event schema implemented.
- [x] Transaction CSV template implemented.
- [x] “Deal value undisclosed” handling specified rather than imputation/fabrication.
- [x] Deduplication and source-evidence rules documented.
- [x] Publication/coverage bias is identified as a required future analysis.
- [x] Full transaction-corpus collection is tracked in `RESEARCH_MILESTONES.md`, not falsely checked here.

## H. AI research integrity

- [x] AI extraction benchmark protocol implemented.
- [x] Ground-truth schema implemented.
- [x] Planned 400–600 document human-label target documented.
- [x] Planned 50–100 document second-annotator subset documented.
- [x] Precision/recall/F1 or field accuracy, hallucination, cost, latency requirements documented.
- [x] Inter-annotator agreement requirement documented.
- [x] Candidate extraction architectures documented.
- [x] Public site does **not** claim the AI benchmark is already completed.
- [x] Deterministic local Evidence Query tool is not misleadingly labeled “AI.”

## I. Immutable forecast accountability

- [x] Forecast-ledger protocol implemented.
- [x] Empty `forecast_ledger.json` committed intentionally.
- [x] Forecasts cannot be presented before transaction milestone gate.
- [x] Future forecast entries must record data vintage and Git commit SHA.
- [x] Issued forecasts are append-only by policy.
- [x] Public site states that no M&A forecast has been issued yet.

## J. Interactive platform

- [x] Professional homepage and research framing implemented.
- [x] Public-data headline metrics implemented.
- [x] State selector implemented.
- [x] Sector selector implemented.
- [x] Year selector implemented.
- [x] Market KPI cards implemented.
- [x] Historical trajectory visualization implemented without chart-library dependency.
- [x] Score decomposition visualization implemented.
- [x] 2023 leaderboard implemented.
- [x] Leaderboard search implemented.
- [x] Point-in-time validation table implemented.
- [x] Holdout/failure interpretation implemented.
- [x] Methodology section implemented.
- [x] Official-source registry implemented.
- [x] Local evidence-query experience implemented.
- [x] Limitations section implemented.
- [x] Forecast-ledger section implemented.
- [x] Light/dark theme toggle implemented.
- [x] Mobile breakpoints implemented.
- [x] Keyboard skip link implemented.
- [x] Form/search controls include labels/ARIA where appropriate.

## K. Research publications / documentation

- [x] Technical research-preview paper implemented with actual generated v0.1 results.
- [x] Practitioner brief implemented.
- [x] Full methodology implemented.
- [x] Data dictionary implemented.
- [x] Limitations document implemented.
- [x] Forecast protocol implemented.
- [x] Transaction schema implemented.
- [x] AI benchmark protocol implemented.
- [x] Reviewer-response log implemented and truthfully states no outside review yet.
- [x] Future research/adoption milestones separated into `RESEARCH_MILESTONES.md`.

## L. Claim / credibility QA

- [x] No claim that the project predicts investment returns.
- [x] No claim that high SRS means “buy this market.”
- [x] No claim that an external professional has adopted the tool yet.
- [x] No claim that professors reviewed the work yet.
- [x] No fake user counts, citations, awards, publications, or transaction counts.
- [x] No “CEO/founder of world-leading institute” inflation.
- [x] Public statements link to official issuing agencies where appropriate.
- [x] Research-derived numbers are generated from committed scripts/artifacts.
- [x] Failure/weakness information is visible, not buried.

## M. Automated release checks

- [x] `scripts/validate_release.py` implemented.
- [x] Required-file checks implemented.
- [x] Panel row/coverage/duplicate checks implemented.
- [x] Score-bound checks implemented.
- [x] Source-manifest checks implemented.
- [x] Browser/latest-data checks implemented.
- [x] Train/validation/holdout checks implemented.
- [x] Baseline/model-comparison checks implemented.
- [x] Failure-analysis check implemented.
- [x] Sensitivity-output checks implemented.
- [x] Forecast-ledger-empty check implemented.
- [x] Claim-boundary checks implemented.
- [x] Official-source-domain checks implemented.
- [x] Accessibility/static-asset checks implemented.
- [x] Placeholder/overclaim checks implemented.
- [x] GitHub Actions validation workflow implemented.

## N. Pre-push final gate

- [x] Python research asset build completes successfully.
- [x] Sensitivity build completes successfully.
- [x] Release validator passes all gates.
- [x] JavaScript syntax check passes.
- [x] Local HTTP smoke test loads app and all data assets with HTTP 200.
- [x] Project ZIP generated from the exact audited release tree.
- [x] No unrelated existing GitHub repository is overwritten to work around repository-creation limitations.


## O. Highest-category technical elevation — v0.2

- [x] Historical replay artifact implemented with realized two-year future establishment growth.
- [x] Replay covers 1978–2021 annual cohorts for aggregate diagnostics.
- [x] 2014–2021 market-level replay dataset implemented for interactive browser inspection.
- [x] Exploratory SRS top-quintile uplift result reported with explicit post-hoc boundary.
- [x] Negative/weak results remain visible rather than selectively removed.
- [x] Four rolling-origin robustness windows implemented using only prior-year training data.
- [x] Fixed HGB specification beats persistence on MAE in all four rolling windows in the generated release.
- [x] Fixed HGB specification beats persistence on Spearman in all four rolling windows in the generated release.
- [x] Fixed HGB specification beats persistence on top-decile precision in all four rolling windows in the generated release.
- [x] Validation-period permutation importance implemented.
- [x] Leave-one-feature-out validation diagnostics implemented.
- [x] Feature diagnostics explicitly labeled post-selection and not used to rewrite the frozen holdout result.
- [x] Model card documents intended use, prohibited use, splits, performance, and limitations.
- [x] Claims/hypothesis registry records supported, unsupported, exploratory, and not-yet-testable statements.
- [x] Unsupported holdout rank-correlation hypothesis retained publicly.
- [x] Reproducibility guide documents full source-to-claim lineage.
- [x] Machine-readable reproducibility manifest records Python/package versions and SHA-256 hashes.

## P. Practitioner workflow elevation — v0.2

- [x] Three-market state comparator implemented for a common sector/year.
- [x] Transparent 2023 evidence screener implemented with user-controlled thresholds.
- [x] Screener results link directly back into the underlying market explorer.
- [x] 2023 score-sensitivity interval surfaced for the selected market.
- [x] Top-quintile stability probability surfaced for the selected market.
- [x] Source-attributed Markdown evidence-brief export implemented.
- [x] Export includes research boundary and exact Census source hash.
- [x] Historical replay table shows what actually happened after the selected historical score.
- [x] 44-cohort uplift visualization implemented without external chart dependencies.
- [x] Rolling-origin results are directly inspectable in the public UI.
- [x] Feature diagnostics are directly inspectable in the public UI.
- [x] Reproducibility evidence chain is directly inspectable in the public UI.
- [x] Final flagship M&A report remains separated as a real future research milestone rather than fabricated now.
