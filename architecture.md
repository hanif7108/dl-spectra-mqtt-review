# Architecture — Hybrid MQTT-Based Regional EEWS

## 1. Scope

Operational deployment design for the IDA-PTW framework on the Indonesian InaTEWS network (BMKG), using MQTT as the inter-service message bus. The design goals are:

- End-to-end latency budget ≤ 3 s from P-onset to published $Sa(T)$ alert.
- Horizontal scalability: each stage runs as an independent service that can be replicated.
- Operational resilience: degrade gracefully if any stage fails (e.g., publish URPD-only binary alert if Stage 2 is down).
- Interoperability with SeedLink / SeisComP via a dedicated bridge.
- Catalog-independent inference (inherits IDA-PTW design).

## 2. Logical view (C4 container diagram, textual)

```
                        ┌──────────────────────────────────────────┐
                        │           BMKG Network (SeedLink)         │
                        └────────────────────┬─────────────────────┘
                                             │
                               ┌─────────────▼──────────────┐
                               │ src/bridge/seedlink_bridge │  service
                               └─────────────┬──────────────┘
                                             │ publish eews/v1/raw/+/+/+
                                             ▼
                         ┌───────────────────────────────────┐
                         │       MQTT broker (EMQX v5)       │
                         │  QoS 1, retained=false for raw    │
                         │  QoS 2, retained=true  for alert  │
                         └────┬──────────────────────────┬───┘
                              │                          │
        sub eews/v1/raw/#     │                          │ sub eews/v1/raw/#
              ┌───────────────▼──────────┐    ┌──────────▼────────────────┐
              │ src/features/physics_    │    │ src/inference/urpd_stage0 │
              │  features (Stage 2 aux)  │    │   (0.5 s window, GBM)     │
              └───────────────┬──────────┘    └──────────┬────────────────┘
                              │ pub eews/v1/feat/...     │ pub eews/v1/pred/urpd/...
                              ▼                          ▼
              ┌───────────────────────────┐    ┌───────────────────────────┐
              │ src/inference/gate_stage1 │    │   src/fusion/             │
              │   (XGBoost intensity)     │    │   decision_engine         │
              └───────────────┬───────────┘    └──────────┬────────────────┘
                              │ pub eews/v1/pred/gate/... │ pub eews/v1/alert/...
                              ▼                           ▼
              ┌───────────────────────────┐    ┌───────────────────────────┐
              │ src/inference/dluhs2_     │    │   External consumers:     │
              │  stage2 (DLUHS2 PSA)      │    │   dashboards, SCADA, SNI- │
              └───────────────────────────┘    │   aware automation hooks  │
                                                └───────────────────────────┘
```

## 3. Component responsibilities

### 3.1 `src/bridge/seedlink_bridge`
Subscribes to BMKG SeedLink streams, re-publishes 100 Hz 1-s chunks (or configurable) to `eews/v1/raw/{net}/{sta}/{cha}`. Stateless. Uses `obspy.clients.seedlink` as the upstream client. Serializes payload as MiniSEED bytes inside an envelope containing monotonic timestamp, ingest wall clock, and sequence number.

### 3.2 `src/features/physics_features`
Subscribes to `eews/v1/raw/#`, maintains a rolling buffer per station (P-window aware). When an URPD positive arrives, computes the 8 physics features (log10 peak, log10 Vs30, log10 dist, τ_c, log10 P_d, log10 CAV, log10 IV2, log10 H/V). Publishes on `eews/v1/feat/{net}/{sta}/{window_s}`. Reuses `src/physics/feature_extractor.py` from DL_Spectra.

### 3.3 `src/inference/urpd_stage0`
Subscribes to `eews/v1/raw/#`. Runs the Ultra-Rapid P-wave Discriminator (GradientBoostingClassifier) on a rolling 0.5-s window with 7 spectral features. Publishes `eews/v1/pred/urpd/{net}/{sta}` with fields `{p_prob, near_field_flag, features_hash}`.

### 3.4 `src/inference/gate_stage1`
Subscribes to `eews/v1/feat/+/+/+` (3 s window variant). Runs the XGBoost intensity classifier (4 classes: Weak, Moderate, Strong, Damaging). Publishes `eews/v1/pred/gate/{net}/{sta}` with `{intensity_class, selected_ptw_s, damaging_recall_conf}`.

### 3.5 `src/inference/dluhs2_stage2`
Subscribes to `eews/v1/feat/+/+/+` and `eews/v1/pred/gate/+/+`. Loads the appropriate DLUHS2 fold-ensemble weights for the selected PTW (3 / 5 / 8 s). Emits 103-period $\log_{10} Sa(T)$ vector on `eews/v1/pred/psa/{net}/{sta}`.

### 3.6 `src/fusion/decision_engine`
Subscribes to all prediction topics for a station, aggregates Stage 0 ∪ Stage 1 ∪ Stage 2 outputs within a tolerance window, converts PSA vector to MMI / PGA / SNI-1726 category, and publishes `eews/v1/alert/{region}/{event_id}` (retained=true, QoS 2).

## 4. Message contract (JSON envelope)

```json
{
  "msg_id": "uuid-v7",
  "produced_at_ns": 1713677123000000000,
  "ingest_at_ns":   1713677123002341000,
  "stage": "stage2",
  "station": {"net": "IA", "sta": "CMJI", "cha": "HNZ"},
  "window_s": 3.0,
  "payload": { "...": "stage-specific, see docs/mqtt_topic_schema.md" }
}
```

Payloads for each stage are defined in Pydantic models under `src/common/schemas.py` and documented in `docs/mqtt_topic_schema.md`.

## 5. ADR log

### ADR-0001 — MQTT as the inter-service bus (Accepted)

**Context.** The IDA-PTW pipeline in its research form is a monolithic Python script. For operational deployment we need to fan out to multiple consumers (dashboard, SCADA, archival), absorb partial failures, and add new stages without touching the core. Options surveyed:

| Option | Pros | Cons |
|---|---|---|
| Kafka | High throughput, durable log | Ops burden, Java JVM, not sensor-friendly |
| MQTT (EMQX / Mosquitto) | Designed for telemetry, QoS 0/1/2, retained messages, low overhead, edge-friendly | No native partition log (we add cold storage via bridge) |
| gRPC streaming | Type-safe, performant | Tight coupling, no pub/sub fan-out |
| ZeroMQ | Low latency | No broker = harder ops |

**Decision.** Use MQTT v5 (EMQX broker) as the internal bus. Retained + QoS 2 on alert topics give operational guarantees; QoS 1 on raw/feature topics bounds latency; shared subscriptions (MQTT v5) enable horizontal scaling of inference workers. The IoT-EEWS literature (Manzano 2017, Tuli 2021, Ruiz-Pinillos 2025) supports this choice.

**Consequences.** (i) adds one infra dep (broker), (ii) requires topic governance, (iii) enables future edge deployment of Stage 0 on low-power MEMS nodes.

### ADR-0002 — Reuse IDA-PTW model weights without retraining (Accepted)

**Context.** DLUHS2 fold-ensemble weights + XGBoost Stage 1/1.5 exist in `/Users/hanif/DL_Spectra/experiments/`. Retraining would waste the ~50 GPU-hour budget already spent.

**Decision.** Import checkpoints as-is for v0. Add a thin adapter layer in `src/inference/` that wraps existing model classes. Retraining is deferred until we need to (a) support 3-channel input end-to-end, (b) add streaming-optimized attention heads, or (c) extend to East Indonesia.

**Consequences.** Deterministic reproduction of IDA-PTW R² = 0.729 in the MQTT-deployed version is a verification requirement before publication.

### ADR-0003 — Catalog-independent inference retained (Accepted)

**Context.** IDA-PTW Stage 1.5 regresses epicentral distance from the 3-s window with 99.87% routing fidelity, removing dependence on BMKG catalog latency (30–60 s).

**Decision.** Carry this property into the MQTT deployment. The bridge must NOT block on catalog availability; catalog hypocenter, if present, is consumed only as an optional validation/prior, not as a routing input.

**Consequences.** All inference stages stay on the sub-3-s budget regardless of catalog latency.

### ADR-0005 — Per-site subscriber topic (Proposed)

**Context.** The default `eews/v1/alert/{region}/{event_id}` payload carries a 103-period $\log_{10} Sa(T)$ vector for the region. External consumers are operational sites (buildings, dams, SCADA controllers) that each care about a **single** $Sa(T_1)$ at their structural fundamental period and need **site-specific correction** (Vs30, local H/V amplification, site–station distance). Forcing every site to do this interpolation themselves creates duplicate code in each edge agent.

**Decision.** Introduce a second, per-site topic:

```
eews/v1/alert_site/{site_id}
```

published by an additional service `src/alerts/site_projector` that:
1. subscribes to `eews/v1/alert/{region}/+` (the regional alert),
2. for each registered site in `configs/sites.yaml` with `site_id, T1, Vs30, lat, lon, nearest_station, SDC`:
   - interpolates $Sa(T_1)$ from the 103-period vector,
   - applies the site correction $\log_{10} Sa_{site} = \log_{10} Sa_{station} + \Delta_{Vs30}(T_1) + \Delta_{dist}(T_1) + \Delta_{HV}(T_1)$,
   - attaches 16/84-percentile bounds using the IDA-PTW $\tau, \phi$ decomposition,
3. publishes a minimal `SiteAlertPayload` on the per-site topic, QoS 2, retained.

**Consequences.** (i) each site only needs to subscribe to a single topic matching its `site_id` — minimal bandwidth, minimal logic on the edge; (ii) site registry becomes authoritative at the region operator; (iii) downstream SNI-1726 automation hooks receive a number, not a vector.

### ADR-0004 — Stage 0 degraded-mode alert (Proposed)

**Context.** If Stage 1 or Stage 2 is temporarily unavailable (e.g., model reload, broker partition), the near-field binary flag from Stage 0 is still life-safety-relevant.

**Decision.** `fusion/decision_engine` publishes a `degraded=true` alert when only Stage 0 is available, carrying the near-field binary flag but no PSA vector. Downstream consumers must handle this mode explicitly (SNI 1726 hooks should treat it as a precautionary shutdown trigger).

**Consequences.** Requires a `reliability_level` enum in the alert schema and client-side handling docs.

## 6. Latency budget (target)

| Stage | Budget (ms) | Rationale |
|---|---|---|
| SeedLink → broker | 50 | 1-s chunk jitter |
| Broker fan-out | 20 | in-memory |
| URPD Stage 0 | 80 | 0.5-s window, GBM |
| Feature extractor | 150 | NumPy |
| Gate Stage 1 | 30 | XGBoost |
| DLUHS2 Stage 2 | 400 | CPU inference, fold ensemble |
| Fusion + publish alert | 50 | |
| **Total** | **≤ 780 ms + P-window** | e.g. 780 ms + 3 s = 3.78 s wall clock |

Stage 0 alone is ≤ 130 ms + 0.5 s = 630 ms, preserving near-field reach.

## 7. Accuracy-improvement plan for $Sa(T)$

The IDA-PTW baseline reports $R^2 = 0.729$ (103-period mean), $\tau = 0.458$, $\phi = 0.598$, $\sigma_{total} = 0.755$. Since $\phi > \tau$, the dominant uncertainty is **intra-event (site-path)**. This dictates the priority ordering below. Each mechanism is scoped to be incremental — we do NOT retrain DLUHS2 from scratch unless explicitly required.

| # | Mechanism | Where it runs | Expected gain | Dependency |
|---|---|---|---|---|
| M1 | Multi-station Bayesian fusion — inverse-variance weighting of $\log_{10} Sa(T)$ from $N$ stations in the same event window | `fusion/decision_engine` | σ reduced by ≈ √N in the $\phi$ component; expected $\sigma$ 0.755 → 0.55 for N=3 | Multi-station quorum already in config |
| M2 | Progressive prediction update (3 s → 5 s → 8 s) — publish revised alert with the same `event_id` as PTW extends | `dluhs2_stage2` + `fusion` | +0.5 % $R^2$ per extra second (IDA-PTW Table 12, high-PGA regime) | Schema-revision field on envelope |
| M3 | Site-specific correction at the edge — $\log_{10} Sa_{site} = \log_{10} Sa_{station} + \Delta_{Vs30} + \Delta_{dist} + \Delta_{HV}$ | `alerts/site_projector` (ADR-0005) | Removes site-amplification bias from the residual; targets $\phi$ reduction | Per-site Vs30 / H/V survey |
| M4 | Ensemble hypocenter — grid-search hypocenter from ≥3 Stage-1.5 distance estimates | `fusion/decision_engine` | Improved $\log_{10}(dist)$ input → +1–2 % $R^2$ | ≥3 active stations |
| M5 | 2-D spectrogram branch in DLUHS2 — parallel branch fused linearly with the 1-D branch | `inference/dluhs2_stage2` + new `dluhs2_hybrid.py` | +3–5 % $R^2$ on PGA/PGV per Münchmeyer 2025, Zhu 2024 | Retrain on same data, same splits |
| M6 | Physics-guided loss + SHAP re-weighting — penalise $Sa(T)$ exceeding GMPE (Abrahamson 2014) ± 2σ | training time only | Tightens 16/84 interval; reduces tail MAE | New training script + GMPE lookup |

### 7.1 Mechanism M1 in detail — multi-station Bayesian fusion

For each period $T$ across $N$ triggering stations, the fused $\log_{10} Sa(T)$ is:

$$\widehat{\log_{10} Sa(T)} = \frac{\sum_{i=1}^{N} w_i(T) \cdot \log_{10} Sa_i(T)}{\sum_{i=1}^{N} w_i(T)}, \quad w_i(T) = \frac{1}{\sigma_i^2(T, d_i, Vs30_i)}$$

where $\sigma_i^2$ is looked up from the IDA-PTW per-period residual table. The fused posterior variance is the inverse of the sum of precisions. This implements the Al Atik et al. (2010) $\tau/\phi$ decomposition operationally.

### 7.2 Mechanism M2 in detail — progressive update contract

On the bus:
1. at $t_{P} + 3\,\text{s}$: first alert published with `revision=1`, `ptw_s=3`, reliability `full_3s`.
2. at $t_{P} + 5\,\text{s}$: same `event_id`, `revision=2`, `ptw_s=5`, reliability `full_5s`.
3. at $t_{P} + 8\,\text{s}$: `revision=3`, `ptw_s=8`, reliability `full_8s` (only for Damaging route).

Consumers MUST idempotently accept later revisions. The retained message is always the latest revision so late joiners see the best estimate.

### 7.3 Mechanism M3 in detail — site correction payload

For each registered site, the projector service publishes:

```jsonc
{
  "site_id": "UI-FT-B",
  "T1_s": 1.8,
  "Sa_site_T1_g": 0.21,
  "Sa_site_T1_p16_g": 0.15,
  "Sa_site_T1_p84_g": 0.29,
  "correction_applied": {
    "delta_Vs30_db": -0.08,
    "delta_dist_db": +0.03,
    "delta_HV_db":  +0.11
  },
  "nearest_station": "CMJI",
  "reliability_level": "full",
  "revision": 2
}
```

### 7.4 Validation strategy

Every mechanism must be validated against the same event-grouped 5-fold CV used in IDA-PTW **plus** the two retrospective events: Cianjur 2022 ($M_w$ 5.6) and Sumedang 2024 ($M_w$ 5.7). A mechanism is accepted only if:
- composite $R^2$ improvement ≥ +1 % on the CV set,
- no regression on Damaging Recall (must stay ≥ 0.91),
- end-to-end latency budget (≤ 780 ms overhead) is preserved.

## 8. Open questions

1. Broker choice EMQX vs Mosquitto — decision pending perf test with 200+ station simulation.
2. TLS + ACL model for multi-tenant operation (BMKG + UI research) — to be decided with BMKG OpSec.
3. Archival strategy: do we replay from MQTT retained or from a SeedLink mirror? Leaning toward SeedLink mirror for bit-exact reproducibility.
