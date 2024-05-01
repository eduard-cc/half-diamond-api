from datetime import datetime
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel

class Status(str, Enum):
    Online = "Online"
    Offline = "Offline"

class Port(BaseModel):
    port: int
    protocol: str
    state: str
    name: Optional[str] = None
    product: Optional[str] = None
    extrainfo: Optional[str] = None
    reason: Optional[str] = None
    version: Optional[str] = None
    conf: Optional[str] = None

class Host(BaseModel):
    ip: str
    mac: str
    vendor: str
    name: str
    last_seen: datetime
    status: Status
    os: Optional[str] = None
    open_ports: Optional[List[Port]] = None