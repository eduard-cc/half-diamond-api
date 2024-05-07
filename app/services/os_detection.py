import nmap
from typing import List, Dict
from services.host_service import HostService
import logging

class OSDetection:
    def __init__(self, host_service: HostService):
        self.nmap = nmap.PortScanner()
        self.host_service = host_service

    def detect_os(self, target_ips: List[str]) -> Dict[str, str]:
        os_by_ip: Dict[str, str] = {}

        for ip in target_ips:
            os = self.detect_target_ip(ip)
            if os is not None and os != 'Unknown':
                os_by_ip[ip] = os

        self.host_service.update_os(os_by_ip)
        return os_by_ip

    def detect_target_ip(self, ip: str) -> str | None:
        try:
            scan_result = self.nmap.scan(hosts=ip, arguments='-O')
        except Exception as e:
            logging.error(f"An error occurred while detecting OS on {ip}: {e}")
            return None

        scan_data = scan_result.get('scan', {}).get(ip, {}).get('osmatch')

        if not scan_data:
            return 'Unknown'

        return scan_data[0]['name']
