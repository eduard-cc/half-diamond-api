import asyncio
from scapy.all import ARP, Ether, srp
import socket
from scapy.all import get_if_hwaddr, conf

class Probe():
    def __init__(self):
        self.is_running: bool = False
        self.THROTTLE: int = 10
        self.local_mac = get_if_hwaddr(conf.iface)
        self.local_ip: str = self.get_local_ip()
        self.subnet: str = self.get_subnet(self.local_ip)

    async def start(self) -> None:
        self.is_running = True
        while self.is_running:
            try:
                self.broadcast_arp_request()
                await asyncio.sleep(self.THROTTLE)
            except Exception as e:
                self.is_running = False
                raise Exception(e)

    def stop(self) -> None:
        self.is_running = False

    def broadcast_arp_request(self) -> None:
        ether = Ether(src=self.local_mac, dst="ff:ff:ff:ff:ff:ff")
        arp = ARP(psrc=self.local_ip, hwsrc=self.local_mac, pdst=self.subnet)
        arp_request = ether / arp
        srp(arp_request, timeout=3, verbose=0)

    def get_local_ip(self) -> str:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("10.0.0.0", 80))
            ip = s.getsockname()[0]
        return ip

    def get_subnet(self, ip) -> str:
        return ip.rsplit('.', 1)[0] + '.0/24'