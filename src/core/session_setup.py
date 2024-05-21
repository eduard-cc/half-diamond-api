from modules.arp_spoof.service import ArpSpoof
from modules.monitor.service import Monitor
from modules.probe.service import Probe
from core.event.handler import EventHandler
from core.host.service import HostService

class Session:
    def __init__(self):
        self.event_handler = EventHandler()
        self.host_service = HostService(self.event_handler)
        self.monitor = Monitor(self.host_service)
        self.probe = Probe()
        self.arp_spoof = ArpSpoof(self.host_service)

session = Session()