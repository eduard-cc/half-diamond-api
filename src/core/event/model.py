from datetime import datetime, timezone
from enum import Enum
from typing import List
from pydantic import BaseModel, Field
from core.host.model import Host

class EventType(str, Enum):
    HOST_NEW = "host.new"
    HOST_SEEN = "host.seen"
    HOST_CONNECTED = "host.connected"
    HOST_DISCONNECTED = "host.disconnected"
    SCAN_TCP = "scan.tcp"
    SCAN_SYN = "scan.syn"
    SCAN_UDP = "scan.udp"
    OS_DETECTED = "os.detected"
    ARP_SPOOF_STARTED = "arp.spoof.started"
    ARP_SPOOF_STOPPED = "arp.spoof.stopped"

class Event(BaseModel):
    time: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    type: EventType
    data: List[Host]

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
        }