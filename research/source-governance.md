# Source Governance & Data Freshness

## Purpose
The Observatory uses two deliberately separate evidence layers:

1. **Historical research layer** — a reproducible Census BDS panel used for the Structural Readiness Score and the current point-in-time forecasting experiments.
2. **Current-context layer** — newer official federal releases that help a user understand the present economic environment without contaminating historical model evaluation.

## Why the layers are separated
A 2023 Structural Readiness Score should not quietly combine a 2023 BDS observation with a 2025 labor statistic or a 2026 macro statistic. Doing that would create a mixed-vintage score that could not have existed at the original point in time and would weaken reproducibility.

Therefore, newer sources are displayed as **context** unless and until they are integrated across historical vintages under the same point-in-time rules used by the research pipeline.

## Registered sources

| Source | Latest context in v0.4 | Role | In current SRS? |
|---|---|---|---|
| U.S. Census Bureau Business Dynamics Statistics | 2023 | Core longitudinal business-structure panel | Yes |
| BLS Quarterly Census of Employment and Wages | Q4 2025 | Employment and wage pulse | No |
| Census Business Formation Statistics | July 2026 | High-frequency business-application / formation pulse | No |
| BEA GDP by State | Q1 2026 | State macroeconomic momentum | No |
| Census County Business Patterns | 2023 | Detailed geography × industry enrichment | No |
| SEC EDGAR | Current filings | Future transaction-evidence source | No |

Machine-readable metadata and exact source URLs are recorded in `data/current_context.json`.

## Current-context headline facts used in the interface

- **QCEW, Q4 2025:** December 2025 national employment was 156.7 million, up 0.2% from December 2024; average weekly wages were $1,569 in Q4 2025, up 4.2% year over year.
- **BFS, July 2026:** 578,926 seasonally adjusted business applications, up 8.1% from June; projected business formations within four quarters were 29,959, up 0.7% from June.
- **BEA, Q1 2026:** real GDP increased in 46 states and the District of Columbia; state annualized changes ranged from +4.5% in Washington to -1.6% in South Dakota.

These are descriptive context facts only. They do not change SRS and are not evidence that any market will experience M&A activity.

## Freshness standard
Every current-context item should record:

- issuing agency;
- product name;
- reference period / latest vintage;
- release date when available;
- exact official source URL;
- role in the platform;
- whether the source is used in SRS or only as context.

## Update standard
When a newer official release is incorporated:

1. update `data/current_context.json`;
2. update the visible freshness matrix on the public site;
3. update any copied headline statistic only after checking it against the official release;
4. preserve the old BDS research panel unless a new BDS release is intentionally rebuilt and revalidated;
5. rerun `scripts/validate_release.py` and `scripts/end_to_end_audit.py`;
6. record the release in the master checklist / repository history.

## Claim boundary
Current context improves timeliness and interpretation. It does **not** turn the current establishment-growth experiment into an M&A forecasting model. Transaction-level acquisition claims still require a verified deal corpus and a separate locked point-in-time M&A evaluation.
