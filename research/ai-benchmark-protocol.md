# AI M&A Extraction Benchmark Protocol

This protocol is implemented as research scaffolding in v0.1; the benchmark must not be described as completed until the required human-labeled corpus exists.

## Target

Evaluate whether an extraction system can convert public acquisition documents into structured fields without inventing missing information.

## Planned ground truth

- 400–600 manually reviewed documents.
- 50–100-document second-annotator reliability subset.
- Adjudication of disagreements before final scoring.

## Fields

- buyer
- target
- announcement date
- state/geography
- sector/industry
- deal value if disclosed
- strategic rationale when explicitly stated

## Candidate systems

1. Structured prompt baseline.
2. Schema-constrained extraction.
3. Retrieval-assisted extraction.
4. Rules + model hybrid.

## Metrics

- exact/normalized field accuracy
- precision, recall, F1 where appropriate
- missing-value honesty / hallucination rate
- cost per document
- latency per document
- inter-annotator agreement on the reliability subset

## Release rule

No benchmark accuracy number may appear on the public website until the labeled source file, scoring code, and result artifact are all committed and reproducible.
