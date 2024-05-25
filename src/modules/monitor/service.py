from threading import Thread
from scapy.all import sniff, ARP
from core.host.service import HostService
import time

class Monitor:
    def __init__(self, host_service: HostService):
        self.is_running: bool = False
        self.sniff_thread: Thread = None
        self.host_service: HostService = host_service

    async def start(self):
        try:
            self.is_running = True
            self.sniff_thread = Thread(target=sniff, kwargs={
                'filter': "arp",
                'prn': self.process_packet,
                'store': 0,
                'stop_filter': lambda _: not self.is_running
            })
            self.sniff_thread.start()
        except Exception as e:
            self.is_running = False
            raise Exception(e)

    def stop(self):
        self.is_running = False
        if self.sniff_thread is not None:
            self.sniff_thread.join()

    def process_packet(self, packet: bytes) -> None:
        if ARP in packet and packet[ARP].op in (1, 2):
            if packet[ARP].hwsrc == "ff:ff:ff:ff:ff:ff":
                return
            host = self.host_service.create_host(packet)
            existing_host = self.host_service.hosts.get(host.mac)
            if existing_host:
                if (time.time() - existing_host.last_seen.timestamp()) >= 1:
                    self.host_service.update_host(host)
            else:
                self.host_service.add_host(host)