# Research Milestones — Real Evidence Only

These are **not release-check boxes** and must not be marked complete merely because code exists. They require real data collection, human verification, outside review, or real-world use.

## Transaction outcome corpus

- [ ] Collect at least 1,000 deduplicated public acquisition events with source URLs.
- [ ] Verify buyer, target, date, geography, and sector for every included event.
- [ ] Record deal value only when publicly disclosed.
- [ ] Conduct publication/coverage-bias analysis.
- [ ] Create frozen transaction-corpus version + checksum.

## AI extraction benchmark

- [ ] Human-label 400–600 public source documents.
- [ ] Obtain an independent second annotation on 50–100 documents.
- [ ] Measure inter-annotator agreement and adjudicate disagreements.
- [ ] Evaluate at least three extraction architectures.
- [ ] Report field-level accuracy/F1, hallucination rate, cost, and latency.
- [ ] Publish failure taxonomy and reproducible scoring code.

## Consolidation forecasting study

- [ ] Define point-in-time acquisition outcome with no future leakage.
- [ ] Predeclare simple baselines.
- [ ] Freeze train / validation / untouched holdout windows.
- [ ] Compare interpretable and machine-learning models.
- [ ] Run feature ablations, weighting sensitivity, and alternative normalizations.
- [ ] Publish uncertainty and sector-level failure analysis.
- [ ] Identify at least one non-obvious result that arises from evidence rather than being chosen in advance.
- [ ] Complete five deep-dive cases: true positive, false positive, false negative, emerging market, mature market.

## Immutable forward test

- [ ] Freeze the first future consolidation forecast in `data/forecast_ledger.json`.
- [ ] Record data vintage + Git commit SHA for every forecast.
- [ ] Leave issued forecasts immutable.
- [ ] Score forecasts when outcomes mature.

## External validation

- [ ] Obtain substantive methodology criticism from at least two academics/data researchers.
- [ ] Obtain substantive product/research criticism from at least three finance practitioners.
- [ ] Record every material critique and response in `research/reviewer-response-log.md`.
- [ ] Run standardized practitioner tasks to test whether the tool improves research quality or speed.
- [ ] Obtain at least one documented real-world research use case; do not count a signup as adoption.

## Publication / recognition

- [ ] Release a final technical paper after transaction validation.
- [ ] Release a concise practitioner report after transaction validation.
- [ ] Submit only to credible research symposia/competitions/venues where fit is genuine.
- [ ] Record external citations, presentations, or adoption only when independently verifiable.
