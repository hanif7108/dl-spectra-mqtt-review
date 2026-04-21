"""
dluhs2_stage2.py — adapter around IDA-PTW DLUHS2 for MQTT deployment.

The DLUHS2 architecture lives in /Users/hanif/DL_Spectra/src/models/dluhs2.py
(single-component Z) and dluhs2_enhanced.py (3-component + aux). We do NOT
re-declare the architecture here; we import it at runtime and attach:

  - fold-ensemble loading
  - PTW-selector driven checkpoint mapping (3 / 5 / 8 s)
  - thread-safe, CPU-first inference
  - PSA payload construction

STATUS: skeleton — wire up once `configs/default.yaml` checkpoints are copied
        into this repo (or confirmed as paths on the host).
"""

from __future__ import annotations

import hashlib
import sys
from pathlib import Path
from typing import Dict, List, Literal

import numpy as np

try:
    import torch
except ImportError:  # pragma: no cover
    torch = None  # type: ignore[assignment]

_IDA_PTW_SRC = Path("/Users/hanif/DL_Spectra")
if str(_IDA_PTW_SRC) not in sys.path:
    sys.path.insert(0, str(_IDA_PTW_SRC))

try:
    from src.models.dluhs2 import DLUHS2  # type: ignore[import-not-found]
except ImportError:  # pragma: no cover
    DLUHS2 = None  # type: ignore[assignment]


from src.common.schemas import PSAPayload


PTW = Literal[3, 5, 8]


class DLUHS2Service:
    """Load fold-ensemble DLUHS2 checkpoints and run CPU inference."""

    def __init__(
        self,
        checkpoints_by_ptw: Dict[PTW, List[str]],
        n_targets: int = 103,
        in_channels: int = 1,
        use_aux: bool = True,
        device: str = "cpu",
    ) -> None:
        if torch is None or DLUHS2 is None:
            raise RuntimeError(
                "torch or DLUHS2 not importable. Check requirements + DL_Spectra path."
            )
        self.device = torch.device(device)
        self.n_targets = n_targets
        self._models: Dict[PTW, List[DLUHS2]] = {}
        self._checksums: Dict[PTW, str] = {}

        for ptw, paths in checkpoints_by_ptw.items():
            models, blob = [], b""
            for p in paths:
                m = DLUHS2(
                    n_targets=n_targets,
                    in_channels=in_channels,
                    use_aux=use_aux,
                ).to(self.device).eval()
                ck = torch.load(p, map_location=self.device)
                state = ck["model"] if isinstance(ck, dict) and "model" in ck else ck
                m.load_state_dict(state)
                models.append(m)
                blob += Path(p).read_bytes()
            self._models[ptw] = models
            self._checksums[ptw] = hashlib.sha1(blob).hexdigest()  # noqa: S324

    @torch.no_grad()  # type: ignore[misc]
    def predict(
        self,
        waveform_z: np.ndarray,
        aux_log10_peak: float,
        ptw: PTW,
    ) -> PSAPayload:
        """Run fold-ensemble mean PSA prediction for a single station window."""
        x = torch.from_numpy(waveform_z.astype(np.float32))[None, None, :].to(
            self.device
        )
        aux = torch.tensor([[aux_log10_peak]], dtype=torch.float32, device=self.device)

        outputs = []
        for m in self._models[ptw]:
            outputs.append(m(x, aux=aux).cpu().numpy())
        mean = np.mean(outputs, axis=0).squeeze(0)

        periods = _default_periods(self.n_targets)
        return PSAPayload(
            log10_psa=mean.tolist(),
            periods_s=periods,
            fold_ensemble_mean=True,
            model_checksum=f"sha1:{self._checksums[ptw]}",
        )


def _default_periods(n: int) -> List[float]:
    """0..5 s inclusive, linearly spaced with n samples."""
    return [float(x) for x in np.linspace(0.0, 5.0, n)]
