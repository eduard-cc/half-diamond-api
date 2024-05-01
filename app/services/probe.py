import asyncio
from scapy.all import ARP, Ether, srp
import socket
from utils.host_builder import HostBuilder
import manuf

class Probe():
    def __init__(self):
        self._running = False
        self.mac_parser = manuf.MacParser()
        self.host_factory = HostBuilder()

    async def start(self):
        self._running = True
        while self._running:
            try:
                self.scan()
                await asyncio.sleep(10)
            except Exception as e:
                print(f"An error occurred during probing: {e}")

    def stop(self):
        self._running = False

    def is_running(self):
        return self._running

    def scan(self):
        subnet = self.get_subnet()
        arp_request = self.create_arp_request(subnet)
        self.send_arp_request(arp_request)

    def get_subnet(self):
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(('8.8.8.8', 80))
            ip = s.getsockname()[0]
        return ip.rsplit('.', 1)[0] + '.0/24'

    def create_arp_request(self, subnet):
        return Ether(dst="ff:ff:ff:ff:ff:ff") / ARP(pdst=subnet)

    def send_arp_request(self, arp_request):
        srp(arp_request, timeout=3, verbose=0)