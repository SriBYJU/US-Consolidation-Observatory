# Deployment

Recommended repository name: **`US-Consolidation-Observatory`**

Recommended visibility: **Public** (the project is designed as open/reproducible research).

## GitHub Pages

After the audited tree is committed to the repository:

1. Open repository **Settings → Pages**.
2. Under **Build and deployment**, choose **Deploy from a branch**.
3. Select `main` and `/ (root)`.
4. Save.

Expected Pages path for the current GitHub account:

`https://sribyju.github.io/US-Consolidation-Observatory/`

The site uses relative paths, so it is compatible with a GitHub Pages project subdirectory.

## Pre-push gate

Run:

```bash
python scripts/validate_release.py
node --check assets/app.js
```

Push only if both return successfully. The GitHub Actions workflow repeats the release validator after push/PR.

## v0.2 pre-deploy gate

Run `python scripts/build_advanced_diagnostics.py`, `node --check assets/app.js`, and `python scripts/validate_release.py`. Deployment is allowed only after all checks pass.
