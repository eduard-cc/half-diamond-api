from enum import Enum
from models.host import Host

class EventType(Enum):
    NEW_HOST = "host.new"
    HOST_SEEN = "host.seen"
    HOST_CONNECTED = "host.connected"
    HOST_DISCONNECTED = "host.disconnected"

class Event:
    def __init__(self, event_type: EventType, event_data: Host):
        self.event_type = event_type
        self.event_data = event_data

class NewHostEvent(Event):
    def __init__(self, host: Host):
        super().__init__(EventType.NEW_HOST, host)

class HostLastSeenUpdatedEvent(Event):
    def __init__(self, host: Host):
        super().__init__(EventType.HOST_SEEN, host)

class HostConnectedEvent(Event):
    def __init__(self, host: Host):
        super().__init__(EventType.HOST_CONNECTED, host)

class HostDisconnectedEvent(Event):
    def __init__(self, host: Host):
        super().__init__(EventType.HOST_DISCONNECTED, host)