# Session log — 2026-04-21

Kickoff session for the Hybrid MQTT-Based Regional EEWS extension of IDA-PTW.

## Decisions taken
- Mount `/Users/hanif/DL_Spectra` read-only to reuse the authoritative IDA-PTW artifacts.
- Adopt MQTT v5 (EMQX target) as the inter-service bus — ADR-0001.
- Reuse IDA-PTW model weights without retraining for v0 — ADR-0002.
- Keep catalog-independent inference — ADR-0003.
- Propose Stage-0-only degraded-mode alerting — ADR-0004.

## Artefacts produced in this session
- `README.md` — overview, layout, status table.
- `docs/architecture.md` — C4 container diagram (textual) + latency budget + ADR log.
- `docs/mqtt_topic_schema.md` — topic tree, QoS, retention, ACL sketch, payload JSON shapes.
- `docs/literature_review.md` — Scopus-flavored bibliography across 4 topics.
- `configs/default.yaml` — broker, ingest, feature, stage 0/1/2, fusion defaults.
- `requirements.txt` — Python runtime and dev deps.
- `src/common/schemas.py` — Pydantic message contracts (envelope + 5 payload types).
- `src/common/logging.py` — structlog bootstrap.
- `src/ingest/waveform_subscriber.py` — paho-mqtt subscriber wrapper.
- `src/features/physics_features.py` — wrapper delegating to IDA-PTW feature extractor.
- `src/inference/urpd_stage0.py`, `gate_stage1.py`, `dluhs2_stage2.py` — service skeletons.
- `src/fusion/decision_engine.py` — alert assembly + degraded-mode logic stub.
- `src/alerts/alert_publisher.py` — QoS 2 retained alert publisher.
- `src/bridge/seedlink_bridge.py` — SeedLink → MQTT bridge stub.
- `simulations/README.md`, `notebooks/README.md` — scaffolding with planned experiments.

## Open items for next session
1. Copy (or symlink) the concrete model artefacts into `models/` so the service skeletons can be wired end-to-end.
2. Stand up a local EMQX/Mosquitto broker and run `notebooks/01_broker_latency_profile.ipynb`.
3. Port the Stage-0 URPD training script from DL_Spectra for reproducibility in this repo.
4. Decide with BMKG which SeedLink stations are in scope for the pilot.
5. Verify 2024–2026 DOIs in `docs/literature_review.md` against Scopus.
