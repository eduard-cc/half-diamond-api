from threading import Thread
from scapy.all import sniff, ARP
from services.host_service import HostService
import time

class Monitor:
    def __init__(self, host_service: HostService):
        self.is_running: bool = False
        self.sniff_thread: Thread = None
        self.host_service: HostService = host_service

    def start_sniffing(self):
        sniff(filter="arp",
              prn=self.process_packet,
              store=0,
              stop_filter=lambda _: not self.is_running)

    async def start(self):
        if self.is_running:
            raise Exception("Monitor is already running")
        try:
            self.is_running = True
            self.sniff_thread = Thread(target=self.start_sniffing)
            self.sniff_thread.start()
        except Exception as e:
            self.is_running = False
            raise Exception(e)

    def stop(self):
        if not self.is_running:
            raise Exception("Monitor is not running")
        self.is_running = False
        if self.sniff_thread is not None:
            self.sniff_thread.join()


    def process_packet(self, packet: bytes) -> None:
        if ARP in packet and packet[ARP].op in (1, 2):
            host = self.host_service.create_host(packet)
            existing_host = self.host_service.hosts.get(host.mac)
            if existing_host:
                if (time.time() - existing_host.last_seen.timestamp()) >= 1:
                    self.host_service.update_host(host)
            else:
                self.host_service.add_host(host)