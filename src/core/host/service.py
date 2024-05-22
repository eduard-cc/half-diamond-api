import asyncio
from datetime import datetime
from typing import Dict, List
from modules.port_scan.model import PortScanType
from core.event.model import Event, EventType
from core.event.handler import EventHandler
from core.host.model import Host, Port, Status
from scapy.all import ARP, conf
import socket
from manuf import manuf, MacParser
from scapy.all import get_if_hwaddr
import platform

class HostService:
    def __init__(self, event_handler: EventHandler):
        self.event_handler: EventHandler = event_handler
        self.mac_parser: MacParser = manuf.MacParser()
        local_host = self.create_local_host()
        self.hosts: Dict[str, Host] = {local_host.mac: local_host}
        self.check_coroutine: asyncio.Task = asyncio.create_task(
            self.check_and_update_offline_hosts())

    async def check_and_update_offline_hosts(self) -> None:
        while True:
            for host in self.hosts.values():
                seconds_since_last_seen = (
                    datetime.now() - host.last_seen).total_seconds()

                if host.status == Status.Online and seconds_since_last_seen > 60:
                    host.status = Status.Offline

                    event = Event(type=EventType.HOST_DISCONNECTED, data=[host])
                    asyncio.create_task(self.event_handler.dispatch(event))
            await asyncio.sleep(30)

    def get_hosts(self) -> List[Host]:
        return list(self.hosts.values())

    def get_hosts_from_ips(self, ips: List[str]) -> List[Host]:
        hosts = []
        for host in self.hosts.values():
            if host.ip in ips:
                hosts.append(host)
        return hosts

    def is_new_host(self, host: Host) -> bool:
        return host.mac not in self.hosts

    def create_host(self, packet: bytes) -> Host:
        vendor = self.mac_parser.get_manuf_long(packet[ARP].hwsrc)
        if vendor is None:
            vendor = 'Unknown'

        gateway_ip = conf.route.route("0.0.0.0")[2]
        hostname = None
        if gateway_ip == packet[ARP].psrc:
            hostname = 'Gateway'

        return Host(
            ip=packet[ARP].psrc,
            mac=packet[ARP].hwsrc,
            vendor=vendor,
            last_seen=datetime.now(),
            status=Status.Online,
            name=hostname
        )

    def create_local_host(self) -> Host:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]

        mac = get_if_hwaddr(conf.iface)
        vendor = self.mac_parser.get_manuf_long(mac)
        if vendor is None:
            vendor = 'Unknown'

        return Host(
            ip=ip,
            mac=mac,
            vendor=vendor,
            last_seen=datetime.now(),
            status=Status.Online,
            name=socket.getfqdn(),
            os=platform.platform(terse=False).replace('-', ' ')
        )

    def update_host(self, host: Host) -> None:
        existing_host = self.hosts[host.mac]
        existing_host.last_seen = datetime.now()

        if existing_host.status == Status.Offline:
            existing_host.status = Status.Online
            event = Event(type=EventType.HOST_CONNECTED, data=[host])
            asyncio.run(self.event_handler.dispatch(event))
        else:
            event = Event(type=EventType.HOST_SEEN, data=[host])
            asyncio.run(self.event_handler.dispatch(event))

    def add_host(self, host: Host) -> None:
        self.hosts[host.mac] = host
        event = Event(type=EventType.HOST_NEW, data=[host])
        asyncio.run(self.event_handler.dispatch(event))

    def update_ports(self, ports_by_ip: Dict[str, List[Port]],
                     scan_type: PortScanType) -> None:
        ip_to_host = {host.ip: host for host in self.hosts.values()}

        for ip, ports in ports_by_ip.items():
            host = ip_to_host.get(ip)
            if host:
                for port in ports:
                    host.open_ports = host.open_ports or []
                    if port not in host.open_ports:
                        host.open_ports.append(port)

                if scan_type == PortScanType.SYN:
                    event = Event(type=EventType.SCAN_SYN, data=[host])
                elif scan_type == PortScanType.TCP:
                    event = Event(type=EventType.SCAN_TCP, data=[host])
                elif scan_type == PortScanType.UDP:
                    event = Event(type=EventType.SCAN_UDP, data=[host])

                asyncio.run(self.event_handler.dispatch(event))

    def update_os(self, os_by_ip: Dict[str, str]) -> None:
        ip_to_host = {host.ip: host for host in self.hosts.values()}

        for ip, os in os_by_ip.items():
            host = ip_to_host.get(ip)
            if host:
                host.os = os
                event = Event(type=EventType.OS_DETECTED, data=[host])
                asyncio.run(self.event_handler.dispatch(event))