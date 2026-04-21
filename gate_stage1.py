"""
gate_stage1.py — Stage 1 XGBoost intensity gate.

Input:  8 IDA-PTW physics features computed over a 3-s window.
Output: GatePayload with intensity class ∈ {Weak, Moderate, Strong, Damaging},
        class probabilities, and the selected PTW (3/5/8 s) for Stage 2.

STATUS: skeleton — wire once the xgb.json gate model is exported from
        /Users/hanif/DL_Spectra/experiments/...
"""

from __future__ import annotations

from typing import Dict, List

import numpy as np

try:
    import xgboost as xgb
except ImportError:  # pragma: no cover
    xgb = None  # type: ignore[assignment]

from src.common.schemas import GatePayload, IntensityClass, PhysicsFeatures


_CLASSES: List[IntensityClass] = ["Weak", "Moderate", "Strong", "Damaging"]
_PTW_BY_CLASS = {"Weak": 3, "Moderate": 3, "Strong": 5, "Damaging": 8}


class GateService:
    def __init__(self, model_path: str, damaging_recall_target: float = 0.91) -> None:
        if xgb is None:
            raise RuntimeError("xgboost not installed")
        booster = xgb.Booster()
        booster.load_model(model_path)
        self._booster = booster
        self._damaging_recall_target = damaging_recall_target

    def predict(self, feats: PhysicsFeatures) -> GatePayload:
        x = np.asarray(
            [
                feats.log10_peak_3ch,
                feats.log10_vs30,
                feats.log10_dist_km,
                feats.tau_c,
                feats.log10_Pd,
                feats.log10_CAV,
                feats.log10_IV2,
                feats.log10_HV,
            ],
            dtype=np.float32,
        ).reshape(1, -1)
        dmat = xgb.DMatrix(x)
        probs = self._booster.predict(dmat).squeeze(0)
        if probs.ndim == 0:
            # Binary booster fallback
            probs = np.array([1 - float(probs), 0.0, 0.0, float(probs)])

        class_probs: Dict[IntensityClass, float] = {
            cls: float(p) for cls, p in zip(_CLASSES, probs)
        }
        pred_class: IntensityClass = max(class_probs, key=class_probs.get)  # type: ignore[arg-type]
        return GatePayload(
            intensity_class=pred_class,
            class_probs=class_probs,
            selected_ptw_s=_PTW_BY_CLASS[pred_class],  # type: ignore[arg-type]
            damaging_recall_conf=self._damaging_recall_target,
        )
