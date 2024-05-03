import threading
from scapy.all import sniff, ARP
from app.services.host_service import HostService
from utils.host_builder import HostBuilder
import time

class Monitor:
    def __init__(self, host_service: HostService):
        self._running: bool = False
        self.host_builder: HostBuilder = HostBuilder()
        self.sniff_thread: threading.Thread = None
        self.host_service: HostService = host_service

    def start_sniffing(self):
        sniff(filter="arp",
              prn=self.process_packet,
              store=0,
              stop_filter=lambda _: not self.is_running())

    async def start(self):
        if self._running:
            raise Exception("Monitor is already running")
        try:
            self._running = True
            self.sniff_thread = threading.Thread(target=self.start_sniffing)
            self.sniff_thread.start()
        except Exception as e:
            self._running = False
            raise Exception(e)

    def stop(self):
        if not self._running:
            raise Exception("Monitor is not running")
        try:
            self._running = False
            if self.sniff_thread is not None:
                self.sniff_thread.join()
        except Exception as e:
            raise Exception(e)

    def is_running(self) -> bool:
        return self._running

    def process_packet(self, packet: bytes) -> None:
        if ARP in packet and packet[ARP].op in (1, 2):
            host = self.host_builder.create_host(packet)
            existing_host = self.host_service.hosts.get(host.mac)
            if existing_host:
                if (time.time() - existing_host.last_seen.timestamp()) >= 1:
                    self.host_service.update_host(host)
            else:
                self.host_service.add_host(host)