import asyncio
from scapy.all import ARP, Ether, srp
import socket

class Probe():
    def __init__(self):
        self.is_running: bool = False
        self.THROTTLE: int = 10
        self.subnet: str = self.get_subnet()

    def get_subnet(self) -> str:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(('8.8.8.8', 80))
            ip = s.getsockname()[0]
        return ip.rsplit('.', 1)[0] + '.0/24'

    async def start(self) -> None:
        if self.is_running:
            raise Exception("Probe is already running")
        self.is_running = True
        while self.is_running:
            try:
                ether = Ether(dst="ff:ff:ff:ff:ff:ff")
                arp = ARP(pdst=self.subnet)
                arp_request = ether / arp
                srp(arp_request, timeout=3, verbose=0)
                await asyncio.sleep(self.THROTTLE)
            except Exception as e:
                self.is_running = False
                raise Exception(e)

    def stop(self) -> None:
        if not self.is_running:
            raise Exception("Probe is not running")
        self.is_running = False