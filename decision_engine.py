"""
decision_engine.py — aggregate URPD + Gate + PSA predictions into an Alert.

Implements ADR-0004 (Stage-0-only degraded mode): if PSA is missing within
`agreement_window_ms` but an URPD positive is present, emit a
`degraded_stage0_only` alert carrying just the near-field binary flag.

STATUS: skeleton — aggregation logic + SNI 1726 mapping to be added once
        the offline replay harness exists in simulations/.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Dict, List, Optional
from uuid import uuid4

import numpy as np

from src.common.schemas import (
    AlertPayload,
    GatePayload,
    PSAPayload,
    ReliabilityLevel,
    URPDPayload,
)


def _mmi_from_log10_psa(log10_psa: List[float]) -> float:
    """
    Rough Wald et al. 1999 PGA→MMI mapping, using log10 PSA at T=0 (≈ PGA).
    Returns a float in [1, 12].
    """
    pga_g = 10 ** log10_psa[0] / 9.81  # convert m/s² to g
    # Wald 1999 linear: MMI = 3.66 log10(PGA_cm/s²) - 1.66
    pga_cm = pga_g * 981.0
    if pga_cm <= 0:
        return 1.0
    mmi = 3.66 * np.log10(pga_cm) - 1.66
    return float(max(1.0, min(12.0, mmi)))


def _sni1726_category(pga_g: float) -> str:
    """Trivial placeholder. Replace with actual SNI 1726:2019 S_DS/S_D1 table."""
    if pga_g < 0.067:
        return "SDC-A"
    if pga_g < 0.133:
        return "SDC-B"
    if pga_g < 0.2:
        return "SDC-C"
    if pga_g < 0.33:
        return "SDC-D"
    return "SDC-E"


def build_alert(
    event_id: str,
    region: str,
    triggered_stations: List[str],
    urpd: URPDPayload,
    gate: Optional[GatePayload],
    psa: Optional[PSAPayload],
    started_at_ns: int,
    now_ns: int,
) -> AlertPayload:
    reliability: ReliabilityLevel = "full" if psa is not None else "degraded_stage0_only"

    if psa is not None:
        mmi = _mmi_from_log10_psa(psa.log10_psa)
        pga_g = 10 ** psa.log10_psa[0] / 9.81
        sni = _sni1726_category(pga_g)
    else:
        # Degraded: near-field binary flag only; coarse default
        mmi = 5.0 if urpd.near_field_flag else 3.0
        pga_g = 0.05
        sni = _sni1726_category(pga_g)

    latency_ms = int((now_ns - started_at_ns) / 1_000_000)

    return AlertPayload(
        event_id=event_id,
        region=region,
        triggered_by_stations=triggered_stations,
        mmi_estimated=mmi,
        pga_g_estimated=pga_g,
        log10_psa=psa.log10_psa if psa is not None else None,
        sni1726_category=sni,
        reliability_level=reliability,
        near_field_flag=urpd.near_field_flag,
        alert_time_utc=datetime.now(tz=timezone.utc),
        latency_ms=latency_ms,
    )
