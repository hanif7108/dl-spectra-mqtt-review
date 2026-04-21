"""
schemas.py — Pydantic message contracts for the DL_Spectra_MQTT bus.

All MQTT payloads on `eews/v1/*` must validate against one of these models.
Topic-to-model mapping:

    eews/v1/raw/{net}/{sta}/{cha}              -> Envelope[RawPayload]
    eews/v1/feat/{net}/{sta}/{window_s}        -> Envelope[FeaturePayload]
    eews/v1/pred/urpd/{net}/{sta}              -> Envelope[URPDPayload]
    eews/v1/pred/gate/{net}/{sta}              -> Envelope[GatePayload]
    eews/v1/pred/psa/{net}/{sta}               -> Envelope[PSAPayload]
    eews/v1/alert/{region}/{event_id}          -> Envelope[AlertPayload]
"""

from __future__ import annotations

from datetime import datetime
from typing import Generic, List, Literal, Optional, TypeVar
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


PayloadT = TypeVar("PayloadT", bound=BaseModel)


# ── Shared ────────────────────────────────────────────────────────────────
class Station(BaseModel):
    net: str = Field(..., description="Network code, e.g. 'IA'")
    sta: str = Field(..., description="Station code, e.g. 'CMJI'")
    cha: Optional[str] = Field(None, description="Channel, required for raw")


class Envelope(BaseModel, Generic[PayloadT]):
    msg_id: UUID
    produced_at_ns: int
    ingest_at_ns: Optional[int] = None
    schema_version: Literal["1.0.0"] = "1.0.0"
    stage: Literal["raw", "feat", "urpd", "gate", "psa", "alert"]
    station: Station
    window_s: Optional[float] = None
    payload: PayloadT


# ── Raw waveform ──────────────────────────────────────────────────────────
class RawPayload(BaseModel):
    sampling_rate_hz: int
    chunk_seconds: float
    start_time_utc: datetime
    minised_b64: str

    @field_validator("sampling_rate_hz")
    @classmethod
    def _srate_ok(cls, v: int) -> int:
        if v not in (50, 100, 200):
            raise ValueError(f"unexpected sampling_rate_hz={v}")
        return v


# ── Physics features (IDA-PTW) ────────────────────────────────────────────
class PhysicsFeatures(BaseModel):
    log10_peak_3ch: float
    log10_vs30: float
    log10_dist_km: float
    tau_c: float
    log10_Pd: float
    log10_CAV: float
    log10_IV2: float
    log10_HV: float


class FeaturePayload(BaseModel):
    window_start_utc: datetime
    window_end_utc: datetime
    p_onset_utc: Optional[datetime] = None
    features: PhysicsFeatures


# ── Stage 0 URPD ──────────────────────────────────────────────────────────
class URPDPayload(BaseModel):
    p_prob: float = Field(..., ge=0.0, le=1.0)
    near_field_flag: bool
    spectral_centroid_hz: float
    features_hash: str


# ── Stage 1 intensity gate ────────────────────────────────────────────────
IntensityClass = Literal["Weak", "Moderate", "Strong", "Damaging"]


class GatePayload(BaseModel):
    intensity_class: IntensityClass
    class_probs: dict[IntensityClass, float]
    selected_ptw_s: Literal[3, 5, 8]
    damaging_recall_conf: float = Field(..., ge=0.0, le=1.0)


# ── Stage 2 DLUHS2 PSA ────────────────────────────────────────────────────
class PSAPayload(BaseModel):
    log10_psa: List[float] = Field(..., min_length=103, max_length=103)
    periods_s: List[float] = Field(..., min_length=103, max_length=103)
    fold_ensemble_mean: bool = True
    model_checksum: str


# ── Alert ─────────────────────────────────────────────────────────────────
ReliabilityLevel = Literal[
    "full",                     # DLUHS2 Stage 2 available, any PTW
    "full_3s",                  # explicit PTW variants for progressive updates
    "full_5s",
    "full_8s",
    "degraded_stage0_only",     # Stage 2 unavailable — Stage 0 flag only
]


class AlertPayload(BaseModel):
    event_id: str
    region: str
    triggered_by_stations: List[str]
    mmi_estimated: float
    pga_g_estimated: float
    log10_psa: Optional[List[float]] = Field(None, min_length=103, max_length=103)
    # Optional 16/84-percentile bounds (M1 Bayesian fusion output)
    log10_psa_p16: Optional[List[float]] = Field(None, min_length=103, max_length=103)
    log10_psa_p84: Optional[List[float]] = Field(None, min_length=103, max_length=103)
    sni1726_category: Optional[str] = None
    reliability_level: ReliabilityLevel
    near_field_flag: bool
    alert_time_utc: datetime
    latency_ms: int
    # Progressive-update bookkeeping (M2): same event_id, monotonically
    # increasing revision. Retained message always carries the latest.
    revision: int = 1
    ptw_s: Optional[Literal[3, 5, 8]] = None


# ── Per-site projection (ADR-0005) ────────────────────────────────────────
class SiteCorrection(BaseModel):
    """Log-space additive corrections applied at the site projector."""
    delta_Vs30_db: float = 0.0
    delta_dist_db: float = 0.0
    delta_HV_db: float = 0.0


class SiteAlertPayload(BaseModel):
    """
    Per-site alert published on eews/v1/alert_site/{site_id}.

    Carries a single Sa(T1) value for the site's fundamental period T1,
    plus 16/84 percentile bounds and the site-specific correction applied.
    """
    site_id: str
    T1_s: float = Field(..., gt=0.0, le=5.0)
    Sa_site_T1_g: float
    Sa_site_T1_p16_g: Optional[float] = None
    Sa_site_T1_p84_g: Optional[float] = None
    correction_applied: SiteCorrection
    nearest_station: str
    reliability_level: ReliabilityLevel
    near_field_flag: bool
    revision: int = 1
    alert_time_utc: datetime
    latency_ms: int
    # Provenance back to the regional alert
    source_event_id: str
    source_region: str


__all__ = [
    "Station",
    "Envelope",
    "RawPayload",
    "PhysicsFeatures",
    "FeaturePayload",
    "URPDPayload",
    "GatePayload",
    "PSAPayload",
    "AlertPayload",
    "SiteCorrection",
    "SiteAlertPayload",
    "IntensityClass",
    "ReliabilityLevel",
]
