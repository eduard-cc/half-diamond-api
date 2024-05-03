import asyncio
from datetime import datetime
from typing import Dict, List
from services.event import NewHostEvent, HostConnectedEvent, HostDisconnectedEvent, HostLastSeenUpdatedEvent
from services.event_handler import EventHandler
from models.host import Host, Status

class HostService:
    def __init__(self, event_handler: EventHandler):
        self.hosts: Dict[str, Host] = {}
        self.event_handler: EventHandler = event_handler
        self.schedule_check_coroutine: asyncio.Task = asyncio.create_task(self.schedule_offline_host_check())

    async def schedule_offline_host_check(self) -> None:
        while True:
            self.check_and_update_offline_hosts()
            await asyncio.sleep(60)

    def get_hosts(self) -> List[Host]:
        return list(self.hosts.values())

    def is_new_host(self, host: Host) -> bool:
        return host.mac not in self.hosts

    def update_host(self, host: Host) -> None:
        existing_host = self.hosts[host.mac]
        existing_host.last_seen = datetime.now()
        if existing_host.status == Status.Offline:
            existing_host.status = Status.Online
            event = HostConnectedEvent(host)
            asyncio.run(self.event_handler.dispatch(event))
        else:
            event = HostLastSeenUpdatedEvent(host)
            asyncio.run(self.event_handler.dispatch(event))

    def add_host(self, host: Host) -> None:
        self.hosts[host.mac] = host
        event = NewHostEvent(host)
        asyncio.run(self.event_handler.dispatch(event))

    def check_and_update_offline_hosts(self) -> None:
        for host in self.hosts.values():
            time_since_last_seen = (datetime.now() - host.last_seen).total_seconds()
            if host.status == Status.Online and time_since_last_seen > 60:
                host.status = Status.Offline
                event = HostDisconnectedEvent(host)
                asyncio.run(self.event_handler.dispatch(event))