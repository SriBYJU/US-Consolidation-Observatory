# Data Dictionary

## Core identifiers

| Field | Meaning |
|---|---|
| `year` | BDS reference year |
| `st` | Two-digit state FIPS code |
| `state_name` | Human-readable state/DC name |
| `sector` | BDS NAICS sector code |
| `sector_name` | Human-readable sector label |

## Direct BDS measures used in the public panel

| Field | Meaning |
|---|---|
| `firms` | BDS firm count |
| `estabs` | BDS establishment count |
| `emp` | BDS employment |
| `estabs_entry_rate` | Establishment entry rate |
| `estabs_exit_rate` | Establishment exit rate |
| `net_job_creation_rate` | Net job creation rate |
| `reallocation_rate` | Gross reallocation rate |

## Derived fields

| Field | Formula / interpretation |
|---|---|
| `firms_per_1000_emp` | `1000 × firms / employment`; fragmentation proxy, not HHI |
| `employees_per_firm` | `employment / firms` |
| `structural_readiness_score` | Weighted within-sector-year percentile summary described in `methodology.md` |
| `score_data_completeness` | Share of six SRS components available |

Missing/suppressed values remain missing. No suppressed value is replaced by zero.
