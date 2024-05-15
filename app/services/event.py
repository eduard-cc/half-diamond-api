from datetime import datetime, timezone
from enum import Enum
from pydantic import BaseModel, Field
from models.host import Host

class EventType(str, Enum):
    HOST_NEW = "host.new"
    HOST_SEEN = "host.seen"
    HOST_CONNECTED = "host.connected"
    HOST_DISCONNECTED = "host.disconnected"
    SCAN_TCP = "scan.tcp"
    SCAN_SYN = "scan.syn"
    SCAN_UDP = "scan.udp"
    OS_DETECTED = "os.detected"

class Event(BaseModel):
    time: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    type: EventType
    data: Host

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
        }