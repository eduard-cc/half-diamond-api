import asyncio
import threading
from datetime import datetime, timedelta
from typing import Dict
from fastapi import WebSocket
from scapy.all import sniff, ARP
from services.host_cache import HostCache
from utils.host_builder import HostBuilder
from models.host import Host, Status

class Monitor:
    def __init__(self, host_cache_file: str):
        self._running: bool = False
        self.websocket: WebSocket = None
        self.host_cache: HostCache = HostCache(host_cache_file, self.websocket)
        self.host_builder: HostBuilder = HostBuilder()
        self.loop: asyncio.AbstractEventLoop = asyncio.get_event_loop()
        self.last_update_time: Dict[str, datetime] = {}
        self.last_websocket_update_time: datetime = datetime.now()

    def start_sniffing(self):
        try:
            sniff(filter="arp",
                  prn=self.process_packet,
                  store=0,
                  stop_filter=lambda _: not self._running)
        except Exception as e:
            print(f"Exception in sniffing thread: {e}")

    async def start(self):
        self._running = True
        sniff_thread = threading.Thread(target=self.start_sniffing)
        sniff_thread.start()
        while self._running:
            self.update_host_statuses()
            await asyncio.sleep(30)

    def stop(self):
        self._running = False

    def is_running(self) -> bool:
        return self._running

    def process_packet(self, packet: bytes) -> None:
        if ARP in packet and packet[ARP].op in (1, 2):
            host = self.host_builder.create_host(packet)
            self.update_host_cache(host)
            self.send_host_cache()

    def update_host_cache(self, host: Host) -> None:
        current_time = datetime.now()
        if (host.mac not in self.last_update_time or
            current_time - self.last_update_time[host.mac] > timedelta(seconds=1)):
            updated = self.host_cache.update([host])
            if updated:
                self.last_update_time[host.mac] = current_time

    def send_host_cache(self) -> None:
        current_time = datetime.now()
        if current_time - self.last_websocket_update_time > timedelta(seconds=1):
            asyncio.run_coroutine_threadsafe(self.host_cache.send(), self.loop)
            self.last_websocket_update_time = current_time

    def update_host_statuses(self) -> None:
        current_time = datetime.now()
        for host in self.host_cache.hosts:
            if (current_time - host.last_seen > timedelta(minutes=1) and
                host.status != Status.Offline):
                host.status = Status.Offline
        self.host_cache.save()