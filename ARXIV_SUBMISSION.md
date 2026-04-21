# arXiv Submission Package — IDA-PTW Manuscript

Step-by-step guide to upload the IDA-PTW manuscript (currently under review at *IEEE Access*) as an arXiv preprint. Once the arXiv ID is assigned (`arXiv:2504.XXXXX` or similar), update reference [30] in the MQTT-Hybrid manuscript with the actual ID before IEEE IoTJ submission.

Target: **eess.SP** (Signal Processing) as primary, **physics.geo-ph** (Geophysics) as secondary.

## 1 · Account and endorsement prerequisites

- Open https://arxiv.org/user/register if you do not yet have an account. Use the same email as the corresponding author (`hanif.andi@ui.ac.id`).
- **Endorsement**: eess.SP does not require endorsement for authors with prior publications. Because your JGR: Solid Earth 2025 paper exists (ref [11] in the MQTT manuscript), you are auto-endorsed. If arXiv prompts for endorsement, request it from a colleague with prior eess.SP or physics.geo-ph submissions (any of the co-authors whose ORCID resolves to indexed publications will do).
- ORCID link: bind `0009-0007-9975-1566` in your arXiv profile; this auto-imports co-author metadata and boosts discoverability.

## 2 · Metadata to paste into arXiv submission form

### Title
```
A Saturation-Aware Multi-Stage Framework for Intensity-Driven Adaptive P-Wave
Time Window Selection in Real-Time Spectral Acceleration Prediction:
Operational Design for the Java-Sunda Subduction Zone
```

### Authors (exact order, matches manuscript byline)

```
Hanif Andi Nugraha (Universitas Indonesia)
Dede Djuhana (Universitas Indonesia; BMKG)
Adhi Harmoko Saputro (Universitas Indonesia)
Sigit Pramono (BMKG)
```

### Abstract (paste verbatim from manuscript §Abstract)

```
Real-time prediction of 5%-damped spectral acceleration Sa(T) across 103
structural periods is the defining challenge of engineering-mode Earthquake
Early Warning Systems (EEWS). Classical P-wave architectures operate at fixed
2-3-second observation windows, incurring two compounding failure modes:
(i) magnitude saturation of canonical parameters (tau_c, P_d) for large
ruptures (M_w > 6.5), and (ii) a near-field blind zone (~38 km) where P-S
travel time is insufficient for alert delivery. This paper introduces the
Intensity-Driven Adaptive P-wave Time Window (IDA-PTW) framework - a
saturation-aware, catalog-independent, four-stage machine learning pipeline
designed for operational deployment on the Indonesian InaTEWS network.

The pipeline cascade consists of: (Stage 0) an Ultra-Rapid P-wave
Discriminator (URPD) using Gradient Boosting on 7 spectral features from a
0.5-second window (AUC = 0.988), reducing the near-field blind zone from
38 km to 11 km for human protection and 4 km for infrastructure; (Stage 1)
an XGBoost intensity gate (93.01% accuracy, Damaging Recall = 91.09%)
routing traces to adaptive windows of 3-8 seconds based on the Feature
Dichotomy paradigm; (Stage 1.5) an XGBoost epicentral distance regressor
achieving 99.87% routing fidelity, enabling fully autonomous operation
without catalog dependency; and (Stage 2) an ensemble of 412 period-wise
XGBoost spectral regressors (4 PTW x 103 periods) anchored on
non-saturating features (CVAD, CAV, Arias Intensity).

Validated on 25,058 three-component accelerograms from 338 events across
the Java-Sunda Trench using event-grouped 5-fold cross-validation, the
framework achieves operational composite R^2 = 0.729 (103-period mean) with
99.44% Golden Time Compliance. Extended statistical characterization
following Al Atik et al. (2010) yields tau = 0.458, phi = 0.598,
sigma_total = 0.755 - confirming intra-event (site-path) variability as the
dominant prediction uncertainty source. Within-factor accuracy of 83.3%
(+-1.0 log10) and 54.4% (+-0.5 log10) is reported. Retrospective validation
on the M_w 5.6 Cianjur 2022 and M_w 5.7 Sumedang 2024 events demonstrates
100% Damaging Recall at Stage 0.
```

### Comments (free-form field)

```
Manuscript concurrently under review at IEEE Access. 40+ pages,
30+ figures, 15+ tables. Companion architecture paper: Nugraha et al.,
"A Hybrid MQTT-Based Inter-Service Architecture for Onsite-Regional EEW
with Blind-Zone Mitigation" (arXiv pending; IEEE IoTJ target).
```

### MSC / ACM / PACS classification

Skip — arXiv eess.SP does not require these.

### Primary category
```
eess.SP
```

### Secondary categories (up to 3)
```
physics.geo-ph
cs.LG
```

Rationale: eess.SP for the signal-processing core (P-wave feature
extraction, spectral regression), physics.geo-ph for the seismological
grounding (Java-Sunda subduction zone, ground-motion modeling), cs.LG for
the machine-learning cascade (Gradient Boosting, XGBoost, event-grouped
cross-validation).

### License
```
CC BY 4.0 (arXiv recommended)
```

This matches the MQTT-Hybrid companion site license and is compatible with
IEEE Access policies.

## 3 · Convert Markdown manuscript to arXiv-ready PDF

arXiv prefers LaTeX source, but PDF-only submissions are accepted. The
fastest path from your existing Markdown manuscript to an arXiv-acceptable
PDF is via Pandoc + a minimal LaTeX template.

### Option A · Pandoc to LaTeX (recommended, allows later edits on arXiv)

```bash
# One-time install (macOS)
brew install pandoc basictex
sudo tlmgr update --self
sudo tlmgr install collection-fontsrecommended collection-latexextra

# Inside the DL_Spectra working folder (the IDA-PTW manuscript lives there)
cd /Users/hanif/DL_Spectra

# Produce a LaTeX source + PDF from the Markdown master
pandoc manuscript_draft_IEEE_Antigravity_revised.md \
    --from markdown+tex_math_dollars \
    --to latex \
    --standalone \
    --pdf-engine=xelatex \
    -V documentclass=article \
    -V geometry:margin=1in \
    -V mainfont="Times New Roman" \
    -V colorlinks=true \
    -o ida_ptw_arxiv.tex

# Render PDF
xelatex ida_ptw_arxiv.tex
xelatex ida_ptw_arxiv.tex   # second pass for TOC and references
```

Produces `ida_ptw_arxiv.tex` (upload source) and `ida_ptw_arxiv.pdf`
(for local review). Upload the `.tex` file plus any figure files to arXiv.

### Option B · Pandoc to PDF direct (faster, no later edits)

```bash
pandoc manuscript_draft_IEEE_Antigravity_revised.md \
    -V geometry:margin=1in \
    -V mainfont="Times New Roman" \
    -V fontsize=11pt \
    --pdf-engine=xelatex \
    -o ida_ptw_arxiv.pdf
```

Upload the `.pdf` directly. arXiv accepts but flags it as "PDF-only".

## 4 · Pre-upload checklist

- [ ] Pandoc-produced PDF renders without missing figures or broken math
- [ ] All figures referenced in text are present in the PDF
- [ ] All tables fit within page bounds (no horizontal overflow)
- [ ] References section is complete and all DOIs are filled
- [ ] Corresponding author email is in the front matter
- [ ] All four ORCID IDs appear in the byline
- [ ] No track-changes artifacts or reviewer comments leaked into the PDF
- [ ] File size under 50 MB (arXiv upload limit for a single submission)

## 5 · Upload procedure

1. Sign in at https://arxiv.org/submit
2. Click **Start a new submission**
3. Select **License**: "CC BY 4.0"
4. Select **Archive**: "Physics", **Subject class**: "eess.SP"
5. Paste metadata from §2 above
6. Upload `ida_ptw_arxiv.pdf` (Option B) or `ida_ptw_arxiv.tex` + any figures
   (Option A)
7. Click **Process**: arXiv renders a preview within 1-3 minutes
8. Review the preview carefully — fix any layout issues before submitting
9. Click **Submit**. You will receive an arXiv identifier within
   2-24 hours, typically `arXiv:2504.NNNNN` (April 2026 series).

## 6 · Post-upload tasks

Once you have the arXiv ID:

1. Update `manuscript_en.md` and `manuscript_id.md` reference [30]:
   Change `arXiv:2504.XXXXX` to the actual assigned ID.
2. Re-embed in `index.html`:
   ```bash
   cd /Users/hanif/DL_Spectra_MQTT/github_pages_site
   python3 rebuild_inline_blob.py  # see below
   git add manuscript_*.md index.html
   git commit -m "chore: update ref [30] with arXiv ID 2504.NNNNN"
   git push
   ```
3. Update the arXiv ID in the IEEE IoTJ cover letter (COVER_LETTER_IEEE_IOTJ.md)
4. Announce the preprint on your Google Scholar / ORCID profile
5. Update the BMKG-UI research page with the arXiv link

## 7 · Rebuild script for step 6.2

Create `rebuild_inline_blob.py` in `github_pages_site/` with contents:

```python
#!/usr/bin/env python3
"""Re-embed manuscript_{en,id}.md into index.html as MANUSCRIPTS global."""
import json, pathlib, re
root = pathlib.Path(__file__).parent
en = (root / "manuscript_en.md").read_text()
id_ = (root / "manuscript_id.md").read_text()
blob = "const MANUSCRIPTS = " + json.dumps({"en": en, "id": id_}, ensure_ascii=False) + ";"

idx = root / "index.html"
html = idx.read_text()
pattern = re.compile(r'const MANUSCRIPTS = \{.*?\};', re.DOTALL)
if not pattern.search(html):
    raise SystemExit("MANUSCRIPTS const not found in index.html")
new_html = pattern.sub(blob, html, count=1)
idx.write_text(new_html)
print(f"Updated {idx} ({len(new_html)//1024} KB)")
```

Make executable and run with `python3 rebuild_inline_blob.py`.

## Timeline expectation

| Step | Duration |
|---|---|
| arXiv account & endorsement check | 1 day |
| Pandoc conversion + review | 1 day |
| arXiv upload + processing | 2-24 hours |
| arXiv ID announcement | within 1 business day after submit |
| Update MQTT manuscript + push | 15 minutes |

Total realistic turnaround: **3-4 business days** from now to arXiv-live
with the MQTT-Hybrid manuscript fully ready for IEEE IoTJ submission.
