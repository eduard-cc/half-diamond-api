import asyncio
from datetime import datetime
from typing import Dict, List
from services.port_scan_type import PortScanType
from services.event import Event, EventType
from services.event_handler import EventHandler
from models.host import Host, Port, Status

class HostService:
    def __init__(self, event_handler: EventHandler):
        self.hosts: Dict[str, Host] = {}
        self.event_handler: EventHandler = event_handler
        self.schedule_check_coroutine: asyncio.Task = asyncio.create_task(self.schedule_offline_host_check())

    async def schedule_offline_host_check(self) -> None:
        while True:
            self.check_and_update_offline_hosts()
            await asyncio.sleep(30)

    def get_hosts(self) -> List[Host]:
        return list(self.hosts.values())

    def is_new_host(self, host: Host) -> bool:
        return host.mac not in self.hosts

    def update_host(self, host: Host) -> None:
        existing_host = self.hosts[host.mac]
        existing_host.last_seen = datetime.now()

        if existing_host.status == Status.Offline:
            existing_host.status = Status.Online
            event = Event(type=EventType.HOST_CONNECTED, data=host)
            asyncio.run(self.event_handler.dispatch(event))
        else:
            event = Event(type=EventType.HOST_SEEN, data=host)
            asyncio.run(self.event_handler.dispatch(event))

    def add_host(self, host: Host) -> None:
        self.hosts[host.mac] = host
        event = Event(type=EventType.HOST_NEW, data=host)
        asyncio.run(self.event_handler.dispatch(event))

    def update_ports(self, ports_by_ip: Dict[str, List[Port]], scan_type: PortScanType) -> None:
        ip_to_host = {host.ip: host for host in self.hosts.values()}

        for ip, ports in ports_by_ip.items():
            host = ip_to_host.get(ip)
            if host:
                for port in ports:
                    host.open_ports = host.open_ports or []
                    if port not in host.open_ports:
                        host.open_ports.append(port)

                if scan_type == PortScanType.SYN:
                    event = Event(type=EventType.SCAN_SYN, data=host)
                elif scan_type == PortScanType.TCP:
                    event = Event(type=EventType.SCAN_TCP, data=host)
                elif scan_type == PortScanType.UDP:
                    event = Event(type=EventType.SCAN_UDP, data=host)

                asyncio.run(self.event_handler.dispatch(event))

    def update_os(self, os_by_ip: Dict[str, str]) -> None:
        ip_to_host = {host.ip: host for host in self.hosts.values()}

        for ip, os in os_by_ip.items():
            host = ip_to_host.get(ip)
            if host:
                host.os = os
                event = Event(type=EventType.OS_DETECTED, data=host)
                asyncio.run(self.event_handler.dispatch(event))

    def check_and_update_offline_hosts(self) -> None:
        for host in self.hosts.values():
            seconds_since_last_seen = (datetime.now() - host.last_seen).total_seconds()
            if host.status == Status.Online and seconds_since_last_seen > 60:
                host.status = Status.Offline
                event = Event(type=EventType.HOST_DISCONNECTED, data=host)
                asyncio.create_task(self.event_handler.dispatch(event))