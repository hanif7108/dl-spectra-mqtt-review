# MQTT Topic Schema — DL_Spectra_MQTT

Topic root: `eews/v1/`. Version bump on any breaking change.

All payloads are JSON-encoded (UTF-8) with a common envelope (see `src/common/schemas.py`). Binary waveforms are embedded as base64 MiniSEED inside the `payload.minised_b64` field.

## 1. Topic tree

| Topic | Direction | QoS | Retained | Producer | Consumer(s) |
|---|---|---|---|---|---|
| `eews/v1/raw/{net}/{sta}/{cha}` | ingest→bus | 1 | false | `src/bridge/seedlink_bridge` | `features`, `inference/urpd_stage0`, archival |
| `eews/v1/feat/{net}/{sta}/{window_s}` | feature→bus | 1 | false | `src/features/physics_features` | `inference/gate_stage1`, `inference/dluhs2_stage2` |
| `eews/v1/pred/urpd/{net}/{sta}` | pred→bus | 1 | false | `src/inference/urpd_stage0` | `fusion/decision_engine` |
| `eews/v1/pred/gate/{net}/{sta}` | pred→bus | 1 | false | `src/inference/gate_stage1` | `fusion/decision_engine`, `dluhs2_stage2` (routing) |
| `eews/v1/pred/psa/{net}/{sta}` | pred→bus | 1 | false | `src/inference/dluhs2_stage2` | `fusion/decision_engine` |
| `eews/v1/alert/{region}/{event_id}` | alert→bus | 2 | true | `src/fusion/decision_engine` | downstream (dashboard, SCADA, SNI) |
| `eews/v1/alert_site/{site_id}` | site-alert→bus | 2 | true | `src/alerts/site_projector` (ADR-0005) | single-subscription edge agents at each site |
| `eews/v1/health/{service}` | health | 0 | true | every service | monitoring |

Wildcards: subscribers use `eews/v1/raw/#` for all raw waveforms, `eews/v1/feat/+/+/3` for 3-second feature streams, etc.

## 2. Envelope schema

```jsonc
{
  "msg_id": "uuid-v7",                 // globally unique
  "produced_at_ns": 1713677123000000000,
  "ingest_at_ns":   1713677123002341000, // broker receive time (stamped by bridge)
  "schema_version": "1.0.0",
  "stage": "raw | feat | urpd | gate | psa | alert",
  "station": {"net": "IA", "sta": "CMJI", "cha": "HNZ"},
  "window_s": 3.0,                      // feature/pred only; null for raw
  "payload": { /* stage-specific, see below */ }
}
```

## 3. Payload shapes

### 3.1 Raw (`stage=raw`)
```jsonc
{
  "sampling_rate_hz": 100,
  "chunk_seconds": 1.0,
  "start_time_utc": "2026-04-21T05:44:12.000Z",
  "minised_b64": "..."                  // MiniSEED record for this chunk
}
```

### 3.2 Feature (`stage=feat`)
```jsonc
{
  "window_start_utc": "2026-04-21T05:44:12.000Z",
  "window_end_utc":   "2026-04-21T05:44:15.000Z",
  "p_onset_utc":      "2026-04-21T05:44:12.130Z",
  "features": {
    "log10_peak_3ch": -1.82,
    "log10_vs30":      2.57,
    "log10_dist_km":   1.91,
    "tau_c":           0.41,
    "log10_Pd":       -3.11,
    "log10_CAV":      -0.95,
    "log10_IV2":      -4.20,
    "log10_HV":        0.08
  }
}
```

### 3.3 URPD Stage 0 (`stage=urpd`)
```jsonc
{
  "p_prob": 0.973,
  "near_field_flag": true,
  "spectral_centroid_hz": 8.2,
  "features_hash": "sha1:..."
}
```

### 3.4 Gate Stage 1 (`stage=gate`)
```jsonc
{
  "intensity_class": "Damaging",        // Weak | Moderate | Strong | Damaging
  "class_probs": {"Weak": 0.01, "Moderate": 0.05, "Strong": 0.12, "Damaging": 0.82},
  "selected_ptw_s": 8,                  // 3 | 5 | 8
  "damaging_recall_conf": 0.91
}
```

### 3.5 DLUHS2 Stage 2 (`stage=psa`)
```jsonc
{
  "log10_psa": [ /* 103 floats, period order ascending 0..5 s */ ],
  "periods_s": [0.0, 0.05, 0.10, /* ... */],
  "fold_ensemble_mean": true,
  "model_checksum": "sha1:..."
}
```

### 3.6 Alert (`stage=alert`, retained)
```jsonc
{
  "event_id": "IA20260421-054412",
  "region": "jawa_barat",
  "triggered_by_stations": ["CMJI", "JAGI", "SPJI"],
  "mmi_estimated": 7.1,
  "pga_g_estimated": 0.18,
  "log10_psa":     [ /* 103 floats — fused median (M1 output) */ ],
  "log10_psa_p16": [ /* 103 floats — 16th percentile bound    */ ],
  "log10_psa_p84": [ /* 103 floats — 84th percentile bound    */ ],
  "sni1726_category": "SDC-D",
  "reliability_level": "full_5s",        // full | full_3s | full_5s | full_8s | degraded_stage0_only
  "near_field_flag": true,
  "alert_time_utc": "2026-04-21T05:44:15.960Z",
  "latency_ms": 1960,
  "revision": 2,                         // progressive update (M2)
  "ptw_s": 5
}
```

### 3.7 Site-projected alert (`eews/v1/alert_site/{site_id}`, retained)

```jsonc
{
  "site_id": "UI-FT-B",                  // e.g. Fakultas Teknik UI Gedung B
  "T1_s": 1.8,
  "Sa_site_T1_g": 0.21,
  "Sa_site_T1_p16_g": 0.15,
  "Sa_site_T1_p84_g": 0.29,
  "correction_applied": {
    "delta_Vs30_db": -0.08,              // log10-space corrections (M3)
    "delta_dist_db": +0.03,
    "delta_HV_db":  +0.11
  },
  "nearest_station": "CMJI",
  "reliability_level": "full_5s",
  "near_field_flag": true,
  "revision": 2,
  "alert_time_utc": "2026-04-21T05:44:16.020Z",
  "latency_ms": 2020,
  "source_event_id": "IA20260421-054412",
  "source_region": "jawa_barat"
}
```

## 4. Retained / clean-start policy

- Only `alert/*` and `health/*` are retained, allowing late joiners (e.g., a dashboard that just connected) to see the most recent state.
- `raw/*`, `feat/*`, `pred/*` are explicitly non-retained — these are streaming and must NOT be replayed stale on reconnect.

## 5. ACL sketch (EMQX)

```
# Ingest service: publish to raw only
user seedlink_bridge
  publish eews/v1/raw/#

# Feature/inference services: subscribe + publish on their own branch
user features
  subscribe eews/v1/raw/#
  publish   eews/v1/feat/#

user inference_urpd
  subscribe eews/v1/raw/#
  publish   eews/v1/pred/urpd/#

# Fusion: broad subscribe, narrow publish
user fusion
  subscribe eews/v1/pred/#
  publish   eews/v1/alert/#

# External consumers: alert only
role consumer
  subscribe eews/v1/alert/#
```
