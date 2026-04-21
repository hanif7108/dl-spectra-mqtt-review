"""
waveform_subscriber.py — utility MQTT subscriber for eews/v1/raw/#.

This module is NOT the SeedLink bridge; see src/bridge/. Its job is only to
wrap a paho-mqtt client for downstream services (features, inference) that
need to consume raw waveform envelopes with type-safe payloads.

Usage (sync):
    from src.ingest.waveform_subscriber import WaveformSubscriber
    sub = WaveformSubscriber(host="127.0.0.1", port=1883)
    sub.on_waveform = handle_waveform       # callable(envelope) -> None
    sub.run()

STATUS: skeleton. To be fleshed out once the broker config is finalised and
        the physics feature extractor is ported from DL_Spectra.
"""

from __future__ import annotations

import json
from typing import Callable, Optional

import paho.mqtt.client as mqtt
from pydantic import ValidationError

from src.common.logging import get_logger
from src.common.schemas import Envelope, RawPayload


log = get_logger(__name__)


class WaveformSubscriber:
    TOPIC_PATTERN = "eews/v1/raw/#"

    def __init__(
        self,
        host: str = "127.0.0.1",
        port: int = 1883,
        client_id: str = "eews_v1_waveform_subscriber",
        keepalive_s: int = 30,
    ) -> None:
        self._client = mqtt.Client(
            mqtt.CallbackAPIVersion.VERSION2, client_id=client_id
        )
        self._client.on_connect = self._on_connect
        self._client.on_message = self._on_message
        self._host = host
        self._port = port
        self._keepalive = keepalive_s
        self.on_waveform: Optional[Callable[[Envelope[RawPayload]], None]] = None

    # ── public API ────────────────────────────────────────────────────
    def run(self) -> None:
        log.info("connecting", host=self._host, port=self._port)
        self._client.connect(self._host, self._port, keepalive=self._keepalive)
        self._client.loop_forever()

    # ── paho callbacks ────────────────────────────────────────────────
    def _on_connect(self, client, userdata, flags, reason_code, properties=None):
        log.info("connected", reason_code=str(reason_code))
        client.subscribe(self.TOPIC_PATTERN, qos=1)

    def _on_message(self, client, userdata, msg):
        try:
            env = Envelope[RawPayload].model_validate_json(msg.payload)
        except ValidationError as exc:
            log.warning("invalid envelope", topic=msg.topic, error=str(exc))
            return

        if self.on_waveform is not None:
            try:
                self.on_waveform(env)
            except Exception:  # noqa: BLE001
                log.exception("on_waveform callback failed")
