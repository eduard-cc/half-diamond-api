from services.monitor import Monitor
from services.probe import Probe
from services.event_handler import EventHandler
from services.host_service import HostService

class Session:
    def __init__(self):
        self.event_handler = EventHandler()
        self.host_service = HostService(self.event_handler)
        self.monitor = Monitor(self.host_service)
        self.probe = Probe()

session = Session()