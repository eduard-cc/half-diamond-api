from datetime import datetime
from enum import Enum
from typing import List
from pydantic import BaseModel

class Status(str, Enum):
    Online = "Online"
    Offline = "Offline"

class Port(BaseModel):
    port: int
    protocol: str
    state: str
    name: str | None = None
    product: str | None = None
    extrainfo: str | None = None
    reason: str | None = None
    version: str | None = None
    conf: str | None = None

class Host(BaseModel):
    ip: str
    mac: str
    vendor: str
    last_seen: datetime
    status: Status
    name: str | None = None
    os: str | None = None
    open_ports: List[Port] | None = None