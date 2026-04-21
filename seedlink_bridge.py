"""
seedlink_bridge.py — SeedLink → MQTT bridge.

Subscribes to an upstream SeedLink server (BMKG production; GEOFON in dev),
buffers 1-second chunks, and republishes them as eews/v1/raw/{net}/{sta}/{cha}
envelopes with base64-encoded MiniSEED payloads.

STATUS: skeleton. Needs:
  - ObsPy `EasySeedLinkClient` wiring
  - back-pressure + drop policy (raw is QoS 1, non-retained; never block)
  - per-station reconnect + lag metrics
"""

from __future__ import annotations

import base64
import io
from datetime import timezone
from time import time_ns
from uuid import uuid4

import paho.mqtt.client as mqtt

from src.common.logging import get_logger
from src.common.schemas import Envelope, RawPayload, Station


log = get_logger(__name__)


class SeedLinkMQTTBridge:
    def __init__(
        self,
        seedlink_host: str,
        seedlink_port: int,
        mqtt_host: str,
        mqtt_port: int,
        agency: str = "BMKG",
        chunk_seconds: float = 1.0,
        sampling_rate_hz: int = 100,
    ) -> None:
        self._sl_host = seedlink_host
        self._sl_port = seedlink_port
        self._chunk_s = chunk_seconds
        self._srate = sampling_rate_hz
        self._agency = agency

        self._mqtt = mqtt.Client(
            mqtt.CallbackAPIVersion.VERSION2, client_id=f"eews_v1_bridge_{uuid4().hex[:8]}"
        )
        self._mqtt.connect(mqtt_host, mqtt_port, keepalive=30)
        self._mqtt.loop_start()

    def _publish_trace(self, net: str, sta: str, cha: str, minised: bytes) -> None:
        env = Envelope[RawPayload](
            msg_id=uuid4(),
            produced_at_ns=time_ns(),
            stage="raw",
            station=Station(net=net, sta=sta, cha=cha),
            payload=RawPayload(
                sampling_rate_hz=self._srate,
                chunk_seconds=self._chunk_s,
                start_time_utc="1970-01-01T00:00:00Z",  # TODO: fill from trace.stats.starttime
                minised_b64=base64.b64encode(minised).decode("ascii"),
            ),
        )
        topic = f"eews/v1/raw/{net}/{sta}/{cha}"
        self._mqtt.publish(topic, env.model_dump_json(), qos=1, retain=False)

    def run(self, streams: list[tuple[str, str, str]]) -> None:
        """
        Run the bridge against the given (net, sta, cha) triples.

        NOTE: this is a stub. The real implementation uses
        obspy.clients.seedlink.easyseedlink.EasySeedLinkClient; not wired yet
        because broker + sample station list must be confirmed with BMKG.
        """
        log.warning(
            "bridge.stub",
            msg="SeedLink wiring not implemented yet. Use replay in simulations/ for now.",
            streams=streams,
        )
