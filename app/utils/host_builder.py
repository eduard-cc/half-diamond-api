from scapy.all import ARP, conf
from datetime import datetime
from models.host import Host, Status
import socket
from getmac import get_mac_address
import manuf

class HostBuilder:
    def __init__(self):
        self.mac_parser = manuf.MacParser()

    def create_host(self, packet):
        gateway_ip = conf.route.route("0.0.0.0")[2]
        default_interface_mac = get_mac_address()
        current_device_name = socket.gethostname()

        vendor = self.mac_parser.get_manuf_long(packet[ARP].hwsrc)
        if vendor is None:
            vendor = 'Unknown'

        hostname = 'None'
        if packet[ARP].psrc == gateway_ip:
            hostname = 'Gateway'
        elif packet[ARP].hwsrc == default_interface_mac:
            hostname = current_device_name

        return Host(
            ip=packet[ARP].psrc,
            mac=packet[ARP].hwsrc,
            vendor=vendor,
            name=hostname,
            last_seen=datetime.now(),
            status=Status.Online
        )