"""
urpd_stage0.py — Ultra-Rapid P-wave Discriminator service.

Loads a pickled sklearn GradientBoostingClassifier trained in IDA-PTW
Stage 0 (0.5-s window, 7 spectral features, AUC ≈ 0.988). Exposes:

  - feature extraction from a 0.5-s trailing window
  - p_prob + near_field_flag emission
  - URPDPayload construction

STATUS: skeleton — to be connected once the Stage 0 pickle is copied
        under models/ or confirmed at a host path.
"""

from __future__ import annotations

import hashlib
import pickle  # noqa: S403 - model files are trusted artefacts
from pathlib import Path
from typing import List

import numpy as np

from src.common.schemas import URPDPayload


class URPDService:
    def __init__(
        self,
        model_path: str,
        p_prob_threshold: float = 0.80,
        near_field_intensity_threshold_log10_pga_ms2: float = -0.5,
    ) -> None:
        blob = Path(model_path).read_bytes()
        self._model = pickle.loads(blob)  # noqa: S301
        self._checksum = hashlib.sha1(blob).hexdigest()  # noqa: S324
        self._p_thr = p_prob_threshold
        self._nf_thr = near_field_intensity_threshold_log10_pga_ms2

    # ── feature extraction (7 spectral features) ──────────────────────
    @staticmethod
    def _spectral_features(acc_z_05s: np.ndarray, dt: float) -> List[float]:
        # FFT spectral features for the 0.5-s window
        n = len(acc_z_05s)
        spec = np.abs(np.fft.rfft(acc_z_05s))
        freq = np.fft.rfftfreq(n, d=dt)
        eps = 1e-12

        power = spec**2
        total = np.sum(power) + eps
        centroid = float(np.sum(freq * power) / total)
        bandwidth = float(np.sqrt(np.sum(((freq - centroid) ** 2) * power) / total))
        # Spectral rolloff at 85%
        cumulative = np.cumsum(power) / total
        idx = int(np.searchsorted(cumulative, 0.85))
        rolloff = float(freq[min(idx, len(freq) - 1)])
        zcr = float(np.mean(np.abs(np.diff(np.sign(acc_z_05s)))) / 2.0)
        geo = float(np.exp(np.mean(np.log(spec + eps))))
        ari = float(np.mean(spec + eps))
        flatness = geo / (ari + eps)
        log_peak = float(np.log10(np.max(np.abs(acc_z_05s)) + eps))
        log_energy = float(np.log10(total))

        return [centroid, bandwidth, rolloff, zcr, flatness, log_peak, log_energy]

    # ── predict ───────────────────────────────────────────────────────
    def predict(self, acc_z_05s: np.ndarray, dt: float) -> URPDPayload:
        feats = self._spectral_features(acc_z_05s, dt)
        X = np.asarray(feats, dtype=np.float32).reshape(1, -1)
        p_prob = float(self._model.predict_proba(X)[0, 1])
        # Simple rule: near-field if p_prob crosses threshold AND log peak is large
        near_field = bool(p_prob >= self._p_thr and feats[5] >= self._nf_thr)
        return URPDPayload(
            p_prob=p_prob,
            near_field_flag=near_field,
            spectral_centroid_hz=float(feats[0]),
            features_hash=f"sha1:{hashlib.sha1(X.tobytes()).hexdigest()}",  # noqa: S324
        )
