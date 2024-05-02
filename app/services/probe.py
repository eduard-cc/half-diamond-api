import asyncio
from scapy.all import ARP, Ether, srp
import socket

class Probe():
    def __init__(self):
        self._running: bool = False

    async def start(self) -> None:
        if self._running:
            raise Exception("Probe is already running")
        self._running = True
        while self._running:
            try:
                self.scan()
                await asyncio.sleep(10)
            except Exception as e:
                self._running = False
                raise Exception(e)

    def stop(self) -> None:
        if not self._running:
            raise Exception("Probe is not running")
        self._running = False

    def is_running(self) -> bool:
        return self._running

    def scan(self) -> None:
        subnet = self.get_subnet()
        arp_request = self.create_arp_request(subnet)
        self.send_arp_request(arp_request)

    def get_subnet(self) -> str:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(('8.8.8.8', 80))
            ip = s.getsockname()[0]
        return ip.rsplit('.', 1)[0] + '.0/24'

    def create_arp_request(self, subnet:str) -> Ether:
        return Ether(dst="ff:ff:ff:ff:ff:ff") / ARP(pdst=subnet)

    def send_arp_request(self, arp_request: Ether) -> None:
        srp(arp_request, timeout=3, verbose=0)