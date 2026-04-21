"""
site_projector.py — per-site Sa(T1) projection service (ADR-0005).

Subscribes to eews/v1/alert/{region}/+ (retained regional alerts), looks up
each registered site in configs/sites.yaml, interpolates Sa(T1) from the
103-period vector, applies edge-side corrections (Vs30, distance, H/V), and
publishes SiteAlertPayload on eews/v1/alert_site/{site_id} (QoS 2, retained).

STATUS: skeleton. Correction tables (delta_Vs30_db(T), delta_dist_db(T))
must be derived from the IDA-PTW per-period residual analysis before
production use.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from time import time_ns
from typing import Any, Dict, List
from uuid import uuid4

import numpy as np
import paho.mqtt.client as mqtt
import yaml

from src.common.logging import get_logger
from src.common.schemas import (
    AlertPayload,
    Envelope,
    SiteAlertPayload,
    SiteCorrection,
    Station,
)


log = get_logger(__name__)


class SiteProjector:
    def __init__(
        self,
        host: str,
        port: int,
        sites_yaml: str,
        client_id: str = "eews_v1_site_projector",
    ) -> None:
        self._sites: List[Dict[str, Any]] = yaml.safe_load(Path(sites_yaml).read_text())["sites"]
        self._client = mqtt.Client(
            mqtt.CallbackAPIVersion.VERSION2, client_id=client_id
        )
        self._client.on_connect = self._on_connect
        self._client.on_message = self._on_message
        self._host = host
        self._port = port

    # ── lifecycle ─────────────────────────────────────────────────────
    def run(self) -> None:
        self._client.connect(self._host, self._port, keepalive=30)
        self._client.loop_forever()

    def _on_connect(self, client, userdata, flags, reason_code, properties=None):
        log.info("site_projector.connected", reason_code=str(reason_code))
        client.subscribe("eews/v1/alert/+/+", qos=2)

    # ── core ──────────────────────────────────────────────────────────
    def _on_message(self, client, userdata, msg):
        try:
            env = Envelope[AlertPayload].model_validate_json(msg.payload)
        except Exception as exc:  # noqa: BLE001
            log.warning("bad alert envelope", error=str(exc))
            return
        alert = env.payload

        for site in self._sites:
            try:
                projected = self._project(alert, site)
            except Exception:
                log.exception("project failed", site_id=site.get("site_id"))
                continue
            self._publish(projected, env.station)

    # ── projection logic ──────────────────────────────────────────────
    @staticmethod
    def _interp_log10_sa(periods: List[float], log10_psa: List[float], T: float) -> float:
        return float(np.interp(T, periods, log10_psa))

    def _project(self, alert: AlertPayload, site: Dict[str, Any]) -> SiteAlertPayload:
        T1 = float(site["T1_s"])

        # Interpolate median + 16/84 percentiles at T1
        # (periods are assumed linearly spaced 0..5 s; upstream sets them)
        n = 103
        periods = list(np.linspace(0.0, 5.0, n))
        if alert.log10_psa is None:
            raise ValueError("cannot project a degraded-mode alert without log10_psa")

        log10_sa_med = self._interp_log10_sa(periods, alert.log10_psa, T1)
        log10_sa_p16 = (
            self._interp_log10_sa(periods, alert.log10_psa_p16, T1)
            if alert.log10_psa_p16 is not None
            else None
        )
        log10_sa_p84 = (
            self._interp_log10_sa(periods, alert.log10_psa_p84, T1)
            if alert.log10_psa_p84 is not None
            else None
        )

        # Edge-side corrections (M3). These Δ's are placeholders; real
        # values come from the IDA-PTW per-period residual regression.
        d_vs30 = self._delta_vs30_db(float(site["Vs30_mps"]), T1)
        d_dist = self._delta_dist_db(float(site["dist_to_station_km"]), T1)
        d_hv = float(site.get("HV_amplification_log10", 0.0))

        log10_sa_med += d_vs30 + d_dist + d_hv
        if log10_sa_p16 is not None:
            log10_sa_p16 += d_vs30 + d_dist + d_hv
        if log10_sa_p84 is not None:
            log10_sa_p84 += d_vs30 + d_dist + d_hv

        # Convert m/s² to g (standard SNI unit)
        sa_g = float(10 ** log10_sa_med / 9.81)
        sa_p16_g = float(10 ** log10_sa_p16 / 9.81) if log10_sa_p16 is not None else None
        sa_p84_g = float(10 ** log10_sa_p84 / 9.81) if log10_sa_p84 is not None else None

        return SiteAlertPayload(
            site_id=str(site["site_id"]),
            T1_s=T1,
            Sa_site_T1_g=sa_g,
            Sa_site_T1_p16_g=sa_p16_g,
            Sa_site_T1_p84_g=sa_p84_g,
            correction_applied=SiteCorrection(
                delta_Vs30_db=d_vs30,
                delta_dist_db=d_dist,
                delta_HV_db=d_hv,
            ),
            nearest_station=str(site["nearest_station"]),
            reliability_level=alert.reliability_level,
            near_field_flag=alert.near_field_flag,
            revision=alert.revision,
            alert_time_utc=datetime.now(tz=timezone.utc),
            latency_ms=alert.latency_ms,
            source_event_id=alert.event_id,
            source_region=alert.region,
        )

    # ── correction tables (placeholder) ──────────────────────────────
    @staticmethod
    def _delta_vs30_db(vs30_mps: float, T: float) -> float:
        """
        Δ log10 Sa correction for a site with Vs30 != reference Vs30.
        Placeholder: log-linear in Vs30 per Boore-Atkinson 2008 generic shape.
        """
        vs_ref = 400.0
        # Simple linear: softer site amplifies long periods
        return -0.25 * np.log10(max(vs30_mps, 50.0) / vs_ref) * (1.0 + 0.5 * T)

    @staticmethod
    def _delta_dist_db(dist_km: float, T: float) -> float:
        """Δ for site-station distance difference. Placeholder = 0 unless
        the projector ever receives a station-centric Sa vector that needs
        re-basing. In M3 this will be derived from IDA-PTW residuals."""
        return 0.0

    # ── publish ──────────────────────────────────────────────────────
    def _publish(self, site_alert: SiteAlertPayload, source_station: Station) -> None:
        env = Envelope[SiteAlertPayload](
            msg_id=uuid4(),
            produced_at_ns=time_ns(),
            stage="alert",
            station=source_station,
            payload=site_alert,
        )
        topic = f"eews/v1/alert_site/{site_alert.site_id}"
        self._client.publish(topic, env.model_dump_json(), qos=2, retain=True)
        log.info(
            "site_alert.published",
            topic=topic,
            site_id=site_alert.site_id,
            Sa_T1_g=site_alert.Sa_site_T1_g,
            revision=site_alert.revision,
        )
