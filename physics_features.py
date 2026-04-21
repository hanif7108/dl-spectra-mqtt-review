"""
physics_features.py — IDA-PTW 8-feature extractor, MQTT-ready wrapper.

Feature computation is NOT re-implemented here; it is delegated to the
authoritative module at:

    /Users/hanif/DL_Spectra/src/physics/feature_extractor.py

This wrapper:
  1) imports that module at runtime (via sys.path injection),
  2) maintains a rolling 15-s waveform buffer per station,
  3) on `on_p_onset`, extracts the 8 features over the requested PTW window,
  4) emits a FeaturePayload envelope for publication on eews/v1/feat/....

STATUS: skeleton — buffer + publish wiring to be completed after running the
        first simulation. The feature contract itself is already frozen in
        src/common/schemas.py :: PhysicsFeatures.
"""

from __future__ import annotations

import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict

import numpy as np

# Delegate to the authoritative IDA-PTW implementation
_IDA_PTW_SRC = Path("/Users/hanif/DL_Spectra")
if str(_IDA_PTW_SRC) not in sys.path:
    sys.path.insert(0, str(_IDA_PTW_SRC))

try:
    from src.physics.feature_extractor import (  # type: ignore[import-not-found]
        compute_tau_c,
        # NOTE: add other imports as the IDA-PTW API is finalized
    )
except ImportError as exc:  # pragma: no cover
    compute_tau_c = None  # type: ignore[assignment]
    _IMPORT_ERROR = exc


from src.common.schemas import PhysicsFeatures


def extract_features(
    acc_z: np.ndarray,
    acc_n: np.ndarray,
    acc_e: np.ndarray,
    dt: float,
    vs30: float,
    dist_km: float,
) -> PhysicsFeatures:
    """
    Compute the 8 IDA-PTW physics features from a 3-component acceleration
    window (units: m/s²).  Intentionally conservative — returns NaN-free
    floats (uses np.log10 with EPS clipping) so that the MQTT payload always
    validates.
    """
    if compute_tau_c is None:
        raise RuntimeError(
            "IDA-PTW physics module not importable. "
            f"Ensure /Users/hanif/DL_Spectra is on sys.path."
        )

    eps = 1e-12

    peak_3ch = float(np.max(np.sqrt(acc_z**2 + acc_n**2 + acc_e**2)))
    log10_peak = float(np.log10(peak_3ch + eps))

    # Velocity via trapezoidal integration
    vel_z = np.cumsum(acc_z) * dt
    disp_z = np.cumsum(vel_z) * dt

    Pd = float(np.max(np.abs(disp_z)))
    CAV = float(np.sum(np.abs(acc_z)) * dt)
    IV2 = float(np.sum(vel_z**2) * dt)

    peak_h = float(np.max(np.sqrt(acc_n**2 + acc_e**2)))
    peak_v = float(np.max(np.abs(acc_z)))
    HV = (peak_h + eps) / (peak_v + eps)

    return PhysicsFeatures(
        log10_peak_3ch=log10_peak,
        log10_vs30=float(np.log10(max(vs30, eps))),
        log10_dist_km=float(np.log10(max(dist_km, eps))),
        tau_c=float(compute_tau_c(acc_z, dt)),
        log10_Pd=float(np.log10(Pd + eps)),
        log10_CAV=float(np.log10(CAV + eps)),
        log10_IV2=float(np.log10(IV2 + eps)),
        log10_HV=float(np.log10(HV + eps)),
    )
