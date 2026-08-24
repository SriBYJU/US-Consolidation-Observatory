# Deployment

Repository: **`US-Consolidation-Observatory`**

This repository uses **GitHub Actions + GitHub Pages**. Large derived datasets are intentionally not committed. Every deployment:

1. downloads the official Census 2023 BDS State × Sector CSV;
2. verifies its SHA-256 against the audited source fingerprint;
3. rebuilds the full 44,574-row research panel and browser artifacts;
4. rebuilds score sensitivity and advanced diagnostics;
5. runs JavaScript syntax checks and the full research release validator;
6. publishes the generated static site to GitHub Pages.

Expected site: `https://sribyju.github.io/US-Consolidation-Observatory/`

## Repository settings

In **Settings → Pages**, set **Source** to **GitHub Actions**.

## Local reproduction

```bash
python -m pip install -r requirements.txt
curl -fsSL https://www2.census.gov/programs-surveys/bds/tables/time-series/2023/bds2023_st_sec.csv -o /tmp/bds2023_st_sec.csv
echo "ba73f1ad58749d57f04c6bb56b0618c92384897a3e9f793de0df7b23f1f1868a  /tmp/bds2023_st_sec.csv" | sha256sum -c -
BDS_SOURCE=/tmp/bds2023_st_sec.csv python scripts/build_research_assets.py
python scripts/run_score_sensitivity.py
python scripts/build_advanced_diagnostics.py
node --check assets/app-core.js
node --check assets/app.js
python scripts/validate_release.py
python -m http.server 8000
```
