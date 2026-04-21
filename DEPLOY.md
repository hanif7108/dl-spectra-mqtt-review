# Deploy guide

Step-by-step commands to publish this repository to **https://hanif7108.github.io/dl-spectra-mqtt-review/**. Copy the commands verbatim in your terminal; replace `hanif7108` with your own GitHub username if different.

## 1 · Create the remote repository

Open `https://github.com/new` in the browser and create a new repository with these exact settings:

| Field | Value |
|---|---|
| Owner | `hanif7108` |
| Repository name | `dl-spectra-mqtt-review` |
| Description | *A Hybrid MQTT-Based Inter-Service Architecture for Onsite-Regional EEWS · IDA-PTW extension for the Java-Sunda Subduction Zone* |
| Visibility | **Public** |
| Initialise with README | **no** (we already have one) |
| .gitignore / license | **no** (already included) |

Click **Create repository**.

## 2 · Push this folder

From the `github_pages_site/` directory on your machine:

```bash
cd /Users/hanif/DL_Spectra_MQTT/github_pages_site

git init -b main
git add .
git commit -m "Initial commit: systems design review + reference implementation"

git remote add origin https://github.com/hanif7108/dl-spectra-mqtt-review.git
git push -u origin main
```

If you prefer SSH instead of HTTPS:
```bash
git remote add origin git@github.com:hanif7108/dl-spectra-mqtt-review.git
```

## 3 · Enable GitHub Pages

1. Open `https://github.com/hanif7108/dl-spectra-mqtt-review/settings/pages`.
2. Under **Source**, choose **Deploy from a branch**.
3. Set **Branch** to `main`, folder to `/ (root)`, click **Save**.
4. After ~30 seconds, GitHub shows:
   > ✓ Your site is live at **https://hanif7108.github.io/dl-spectra-mqtt-review/**

## 4 · Sanity check

Visit the URL and verify:

- [ ] Hero header renders in dark blue gradient, `INTERNAL REVIEW` banner visible.
- [ ] Sticky nav shows 11 tabs and scrolls smoothly to each section.
- [ ] Overview section loads seven metric cards; clicking one opens a modal.
- [ ] Mermaid container diagram in *Architecture* renders (not plain text).
- [ ] Chart.js latency bar chart and accuracy line chart both render.
- [ ] Manuscript preview under *Manuscript Preview* loads via marked.js.
- [ ] All nine download links in *Download & Explore* resolve (no 404).
- [ ] Bilingual toggle (top-right) swaps EN ↔ ID for nav, cards, charts, and manuscript.

## 5 · Optional · GitHub Actions auto-deploy

For future zero-click deploys, add `.github/workflows/pages.yml` (see the `pages.yml` file in this folder). It publishes on every push to `main` using the modern GitHub Pages Actions flow — no branch-based source needed.

## 6 · Update the manuscript reference

When IDA-PTW is accepted at *IEEE Access*, update reference **[30]** in `manuscript.md` to the DOI, and replace the *"submitted April 2026"* note with the accepted-year citation.

## Troubleshooting

| Symptom | Fix |
|---|---|
| Site 404 after push | Wait 1-2 min after enabling Pages; first build takes longer. |
| Mermaid / Chart.js missing | Network blocks `cdnjs.cloudflare.com` or `cdn.jsdelivr.net`; whitelist or self-host. |
| Bilingual toggle only works for headings | Modal body text is language-specific in JS `modalData` — no action needed. |
| Reviewer flags `computer://` links | Already removed; all links are relative. |
| Site served with Jekyll errors | `.nojekyll` file disables Jekyll; confirm it's committed at repo root. |
