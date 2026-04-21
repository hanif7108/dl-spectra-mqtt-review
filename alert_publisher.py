"""
alert_publisher.py — MQTT publisher for eews/v1/alert/{region}/{event_id}.

QoS 2, retained=true (late-joining consumers see the current active alert).
"""

from __future__ import annotations

import json
from uuid import uuid4
from time import time_ns

import paho.mqtt.client as mqtt

from src.common.logging import get_logger
from src.common.schemas import AlertPayload, Envelope, Station


log = get_logger(__name__)


class AlertPublisher:
    def __init__(
        self,
        host: str = "127.0.0.1",
        port: int = 1883,
        client_id: str = "eews_v1_alert_publisher",
    ) -> None:
        self._client = mqtt.Client(
            mqtt.CallbackAPIVersion.VERSION2, client_id=client_id
        )
        self._host = host
        self._port = port

    def connect(self) -> None:
        self._client.connect(self._host, self._port, keepalive=30)
        self._client.loop_start()

    def publish(
        self,
        alert: AlertPayload,
        source_station: Station,
    ) -> None:
        env = Envelope[AlertPayload](
            msg_id=uuid4(),
            produced_at_ns=time_ns(),
            stage="alert",
            station=source_station,
            payload=alert,
        )
        topic = f"eews/v1/alert/{alert.region}/{alert.event_id}"
        body = env.model_dump_json()
        result = self._client.publish(topic, body, qos=2, retain=True)
        log.info(
            "alert.published",
            topic=topic,
            event_id=alert.event_id,
            reliability=alert.reliability_level,
            latency_ms=alert.latency_ms,
            mid=result.mid,
        )
