from datetime import datetime, timedelta
import json
import os
from typing import List
from fastapi import WebSocket
from fastapi.websockets import WebSocketState
from utils.date_time_encoder import DateTimeEncoder
from models.host import Host

class HostCache:
    def __init__(self, websocket: WebSocket = None):
        self.filename = "host_cache.json"
        self.websocket = websocket
        self.hosts = self.load()

    def load(self) -> List[Host]:
        try:
            with open(self.filename, 'r') as f:
                data = json.load(f)
                return [Host(**host) for host in data]
        except FileNotFoundError:
            return []
        except json.JSONDecodeError:
            # Overwrite the file with an empty list
            with open(self.filename, 'w') as f:
                json.dump([], f)
            return []

    def update(self, new_hosts: List[Host]) -> bool:
        existing_hosts = {host.mac: host for host in self.hosts}
        changed = False
        for new_host in new_hosts:
            if new_host.mac in existing_hosts:
                index = self.hosts.index(existing_hosts[new_host.mac])
                time_difference = new_host.last_seen - self.hosts[index].last_seen
                if (time_difference > timedelta(seconds=1) or
                    self.hosts[index].status != new_host.status):
                    self.hosts[index].last_seen = new_host.last_seen
                    self.hosts[index].status = new_host.status
                    changed = True
            else:
                self.hosts.append(new_host)
                changed = True
        return changed

    async def send(self):
        data = [host.model_dump() for host in self.hosts]
        if self.websocket and self.websocket.application_state == WebSocketState.CONNECTED:
            data_str = json.dumps(data, cls=DateTimeEncoder)
            await self.websocket.send_text(data_str)

    def save(self):
        data = [host.model_dump() for host in self.hosts]
        with open(self.filename, 'w') as f:
            json.dump(data, f, cls=DateTimeEncoder)