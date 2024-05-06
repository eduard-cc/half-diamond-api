from enum import Enum
from models.host import Host

class EventType(Enum):
    HOST_NEW = "host.new"
    HOST_SEEN = "host.seen"
    HOST_CONNECTED = "host.connected"
    HOST_DISCONNECTED = "host.disconnected"
    SCAN_TCP = "scan.tcp"
    SCAN_SYN = "scan.syn"
    SCAN_UDP = "scan.udp"

class Event:
    def __init__(self, type: EventType, data: Host):
        self.type = type
        self.data = data


class NewHostEvent(Event):
    def __init__(self, host: Host):
        super().__init__(EventType.HOST_NEW, host)

class HostSeenEvent(Event):
    def __init__(self, host: Host):
        super().__init__(EventType.HOST_SEEN, host)

class HostConnectedEvent(Event):
    def __init__(self, host: Host):
        super().__init__(EventType.HOST_CONNECTED, host)

class HostDisconnectedEvent(Event):
    def __init__(self, host: Host):
        super().__init__(EventType.HOST_DISCONNECTED, host)


class TcpScanEvent(Event):
    def __init__(self, host: Host):
        super().__init__(EventType.SCAN_TCP, host)

class SynScanEvent(Event):
    def __init__(self, host: Host):
        super().__init__(EventType.SCAN_SYN, host)

class UdpScanEvent(Event):
    def __init__(self, host: Host):
        super().__init__(EventType.SCAN_UDP, host)