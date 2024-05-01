import nmap
from typing import List, Dict
from services.host_cache import HostCache

class OSDetection:
    def __init__(self):
        self.nmap = nmap.PortScanner()
        self.host_cache = HostCache('host_cache.json')

    def detect_os(self, target_ips: List[str]) -> Dict[str, str]:
        os_dict = {}
        for target_ip in target_ips:
            try:
                scan_result = self.nmap.scan(target_ip, arguments='-O')
                if (target_ip in scan_result['scan'] and
                    'osmatch' in scan_result['scan'][target_ip] and
                    scan_result['scan'][target_ip]['osmatch']):
                    os_name = scan_result['scan'][target_ip]['osmatch'][0]['name']
                else:
                    os_name = 'Unknown'
                os_dict[target_ip] = os_name

                # Update the host_cache with the OS
                for host in self.host_cache.hosts:
                    if host.ip == target_ip:
                        host.os = os_name
            except Exception as e:
                print(f"An error occurred while detecting OS on {target_ip}: {e}")

        self.host_cache.save()
        return os_dict