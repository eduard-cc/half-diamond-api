import asyncio
import threading
from datetime import datetime, timedelta
from fastapi import WebSocket
from scapy.all import sniff, ARP
from queue import Queue
from services.host_cache import HostCache
from utils.host_builder import HostBuilder
from models.host import Status
import manuf

class Monitor:
    def __init__(self):
        self._running = False
        self.websocket: WebSocket = None
        self.host_cache = HostCache('host_cache.json', self.websocket)
        self.mac_parser = manuf.MacParser()
        self.host_builder = HostBuilder()
        self.queue = Queue()
        self.loop = asyncio.get_event_loop()
        self.last_update_time = {}
        self.last_websocket_update_time = datetime.now()

    def start_sniffing(self):
        sniff(filter="arp",
              prn=self.process_packet,
              store=0,
              stop_filter=lambda _: not self._running)

    async def start(self):
        self._running = True
        sniff_thread = threading.Thread(target=self.start_sniffing)
        sniff_thread.start()
        while self._running:
            self.update_host_statuses()
            await asyncio.sleep(30)

    def stop(self):
        self._running = False

    def is_running(self):
        return self._running

    def process_packet(self, packet):
        if ARP in packet and packet[ARP].op in (1, 2):
            host = self.host_builder.create_host(packet)
            current_time = datetime.now()
            if (host.mac not in self.last_update_time or
                current_time - self.last_update_time[host.mac] > timedelta(seconds=1)):
                print(host)
                updated = self.host_cache.update([host])
                if updated and current_time - self.last_websocket_update_time > timedelta(seconds=1):
                    asyncio.run_coroutine_threadsafe(self.host_cache.send(), self.loop)
                    self.last_websocket_update_time = current_time
                self.last_update_time[host.mac] = current_time

    def update_host_statuses(self):
        for host in self.host_cache.hosts:
            if datetime.now() - host.last_seen > timedelta(minutes=1):
                host.status = Status.Offline
        self.host_cache.save()