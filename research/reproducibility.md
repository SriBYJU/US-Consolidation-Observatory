# Reproducibility & Evidence Lineage

The Observatory is designed so a numerical claim can be traced from source to display.

## Evidence chain

1. **Official source** — U.S. Census Bureau BDS State × Sector CSV.
2. **Source fingerprint** — SHA-256 and source metadata in `data/source_manifest.json`.
3. **Deterministic build** — `scripts/build_research_assets.py` cleans suppressions, derives variables, builds SRS, and runs the locked model evaluation.
4. **Sensitivity build** — `scripts/run_score_sensitivity.py` runs 1,000 deterministic weight perturbations.
5. **Advanced diagnostics** — `scripts/build_advanced_diagnostics.py` produces historical replay, rolling-origin robustness, feature diagnostics, and the reproducibility fingerprint.
6. **Derived artifacts** — versioned JSON/CSV artifacts generated in `/data` during CI/deployment.
7. **Release validator** — `scripts/validate_release.py` checks integrity, claim boundaries, required outputs, and public-site wiring.
8. **Public display** — `assets/app.js` is a lightweight loader; `assets/app-core.js` and the audited `assets/app-ui.js` render generated artifacts without silently recomputing research claims in the browser.

## Rebuild commands

```bash
BDS_SOURCE=/path/to/bds2023_st_sec.csv python scripts/build_research_assets.py
python scripts/run_score_sensitivity.py
python scripts/build_advanced_diagnostics.py
python scripts/validate_release.py
```

## Environment fingerprint

`data/reproducibility_manifest.json` records Python/package versions plus SHA-256 hashes for core scripts and research artifacts. Future immutable forecasts will additionally store the Git commit SHA.

## Why this matters

A polished interface is not evidence. The research claim is the combination of source data, transformations, model protocol, frozen output, and documented limitations. The UI is only a view over that evidence chain.
