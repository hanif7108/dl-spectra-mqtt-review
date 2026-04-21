# DL_Spectra_MQTT · Systems Design Review

> 🔗 Live site: **https://hanif7108.github.io/dl-spectra-mqtt-review/**

A hybrid MQTT-based inter-service architecture for onsite–regional Earthquake Early Warning System (EEWS) with blind-zone mitigation, extending the **IDA-PTW** framework for the Java–Sunda Subduction Zone (Indonesian InaTEWS pilot).

## Authors

| Name | Affiliation | ORCID |
|---|---|---|
| Hanif Andi Nugraha\* | Department of Physics, Universitas Indonesia | 0009-0007-9975-1566 |
| Dede Djuhana | Universitas Indonesia & BMKG | 0000-0002-2025-0782 |
| Adhi Harmoko Saputro | Universitas Indonesia | 0000-0001-6651-0669 |
| Sigit Pramono | BMKG | 0009-0000-5684-282X |

\*Corresponding author: `hanif.andi@ui.ac.id`

## Contribution

This work addresses a research gap identified in April 2026: **no peer-reviewed publication jointly treats** (A) MQTT as inter-service messaging substrate, (B) hybrid onsite–regional EEWS design, and (C) explicit blind-zone mitigation grounded in P–S travel-time geometry. The closest adjacent prior work reaches only two of the three properties (Pierleoni et al. 2023 for A∧B; Wu et al. 2022 P-Alert for B∧C).

## What's in this repository

This is the companion artefact repository for a manuscript targeted at **IEEE Internet of Things Journal**. It contains:

### Documentation

| File | Description |
|---|---|
| [`manuscript.md`](manuscript.md) | Full 7 100-word IEEE IoTJ manuscript draft with 40 references and 6 tables |
| [`architecture.md`](architecture.md) | C4 container view, latency budget, five ADRs, accuracy-improvement plan |
| [`mqtt_topic_schema.md`](mqtt_topic_schema.md) | Complete MQTT topic tree, QoS, retention policy, ACL sketch, payload JSON shapes |
| [`literature_review.md`](literature_review.md) | Scopus-indexed references across four topics plus the three-way gap analysis |
| [`session_log.md`](session_log.md) | Chronological record of architecture decisions taken in the design session |

### Interactive visualisations

| File | Description |
|---|---|
| [`index.html`](index.html) | Single-page review site — 11 sections with bilingual EN/ID toggle, Chart.js charts, Mermaid diagrams, modal explanations |
| [`architecture_diagrams.html`](architecture_diagrams.html) | Six Mermaid diagrams: system view, topic tree, per-event sequence, accuracy mechanisms, subscriber contract, latency budget |
| [`github_pr_review.html`](github_pr_review.html) | Simulated GitHub pull-request review page with eight review threads and three alternative-implementation dossiers |

### Reference implementation (Python 3.10+)

| File | Description |
|---|---|
| [`schemas.py`](schemas.py) | Pydantic v2 envelope + seven payload types (RawPayload, PhysicsFeatures, URPDPayload, GatePayload, PSAPayload, AlertPayload, SiteAlertPayload) |
| [`logging.py`](logging.py) | Structured logging bootstrap (structlog) shared by every service |
| [`seedlink_bridge.py`](seedlink_bridge.py) | SeedLink → MQTT bridge service skeleton |
| [`waveform_subscriber.py`](waveform_subscriber.py) | MQTT subscriber for raw waveform topics |
| [`physics_features.py`](physics_features.py) | Wrapper around the IDA-PTW eight-feature physics extractor |
| [`urpd_stage0.py`](urpd_stage0.py) | Ultra-Rapid P-wave Discriminator (0.5 s window · AUC 0.988) |
| [`gate_stage1.py`](gate_stage1.py) | XGBoost four-class intensity gate with PTW routing |
| [`dluhs2_stage2.py`](dluhs2_stage2.py) | DLUHS2 fold-ensemble service for 103-period Sa(T) prediction |
| [`decision_engine.py`](decision_engine.py) | Fusion engine — multi-station Bayesian fusion + degraded-mode alerting |
| [`alert_publisher.py`](alert_publisher.py) | Regional alert publisher (QoS 2, retained) |
| [`site_projector.py`](site_projector.py) | Per-site Sa(T₁) projector (ADR-0005) |
| [`default.yaml`](default.yaml) | Default configuration for broker, ingest, inference, fusion |
| [`sites.yaml`](sites.yaml) | Example site registry (Universitas Indonesia, BMKG Jakarta Ops, Jembatan Cikubang) |
| [`requirements.txt`](requirements.txt) | Python runtime dependencies |

## Architecture at a glance

```
BMKG SeedLink ─▶ bridge ─┐
                          │  eews/v1/raw/{net}/{sta}/{cha}
                          ▼
                     MQTT v5 broker
                          │
          ┌───────────────┼────────────────┐
          ▼               ▼                ▼
      features/       inference/        bridge/
      physics         urpd_stage0       (archival mirror)
          │               │
          ▼               ▼
      eews/v1/feat/...  eews/v1/pred/urpd/...
                          │
                          ▼
                     fusion/decision_engine
                          │
                          ▼
                     eews/v1/alert/...   (QoS 2, retained)
                          │
                          ▼
                     site_projector
                          │
                          ▼
                     eews/v1/alert_site/{site_id}
```

## Headline numbers

| Metric | Value | Source |
|---|---|---|
| Blind-zone radius reduction | 38 km → 4–11 km | §V · case studies |
| Stage-0 near-field alert latency | ≈ 630 ms | Table III · latency budget |
| First full alert wall clock (PTW 3 s) | ≈ 3.78 s | Table III |
| IDA-PTW $R^2$ baseline (103-period mean) | 0.729 | Nugraha et al. 2026 |
| $\sigma_{total}$ baseline → projected with M1 (N=3) | 0.755 → 0.55 | §IV · M1 analysis |
| Damaging Recall (Stage 1 gate) | 91.1 % | IDA-PTW Table 11 |
| Topic classes formally specified | 8 | §III · Table II |
| Architecture Decision Records | 5 | §III · ADR log |

## Citing

If you find this work useful, please cite (BibTeX provided when the manuscript is accepted):

```
@misc{nugraha2026mqtthybridEEWS,
  author  = {Hanif Andi Nugraha and Dede Djuhana and Adhi Harmoko Saputro and Sigit Pramono},
  title   = {A Hybrid {MQTT}-Based Inter-Service Architecture for Onsite--Regional
             Earthquake Early Warning with Blind-Zone Mitigation: Systems Design for
             the Java--Sunda Subduction Zone},
  year    = {2026},
  note    = {Manuscript submitted to IEEE Internet of Things Journal},
  url     = {https://hanif7108.github.io/dl-spectra-mqtt-review/}
}
```

## License

Code: **MIT**. Documentation and figures: **CC-BY-4.0**. See `LICENSE` for details.

## Acknowledgements

This is a companion repository to the upstream IDA-PTW framework (manuscript submitted to *IEEE Access*, April 2026) authored by the same team. The MQTT architecture reuses the IDA-PTW model weights unchanged (ADR-0002) and focuses the novelty on the messaging substrate.
