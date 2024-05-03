import nmap
from typing import List, Dict
from models.host import Port

class PortScan:
    def __init__(self):
        self.nmap = nmap.PortScanner()

    def scan_ports(self, target_ips: List[str], scan_type: str) -> Dict[str, List[Port]]:
        open_ports_dict = {}
        for target_ip in target_ips:
            try:
                open_ports = self.scan_target(target_ip, scan_type)
                open_ports_dict[target_ip] = open_ports

                # for host in self.host_cache.hosts:
                #     if host.ip == target_ip:
                #         host.open_ports = open_ports
            except Exception as e:
                print(f"An error occurred while scanning ports on {target_ip}: {e}")

        # self.host_cache.save()
        return open_ports_dict

    def scan_target(self, target_ip: str, scan_type: str) -> List[Port]:
        arguments = self.get_scan_arguments(scan_type)
        scan_result = self.nmap.scan(target_ip, arguments)
        open_ports = []
        if 'tcp' in scan_result['scan'].get(target_ip, {}):
            for port, port_info in scan_result['scan'][target_ip]['tcp'].items():
                if port_info['state'] == 'open':
                    open_ports.append(Port(
                        port=int(port),
                        protocol='tcp',
                        state=port_info['state'],
                        name=port_info.get('name'),
                        product=port_info.get('product'),
                        extrainfo=port_info.get('extrainfo'),
                        reason=port_info.get('reason'),
                        version=port_info.get('version'),
                        conf=port_info.get('conf')
                    ))
        return open_ports

    def get_scan_arguments(self, scan_type: str) -> str:
        if scan_type == 'TCP':
            return '-sT'
        elif scan_type == 'SYN':
            return '-sS'
        elif scan_type == 'UDP':
            return '-sU'
        else:
            raise ValueError(f"Invalid scan type: {scan_type}")