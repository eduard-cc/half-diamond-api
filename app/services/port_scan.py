import logging
import nmap
from typing import Any, List, Dict
from services.host_service import HostService
from models.host import Port
from services.port_scan_type import PortScanType

class PortScan:
    def __init__(self, host_service: HostService):
        self.nmap = nmap.PortScanner()
        self.host_service: HostService = host_service

    def scan_ports(self, target_ips: List[str], scan_type: PortScanType) -> Dict[str, List[Port]]:
        ports_by_ip: Dict[str, List[Port]] = {}

        for target_ip in target_ips:
            open_ports = self.scan_target_ip(target_ip, scan_type)
            if open_ports is not None:
                ports_by_ip[target_ip] = open_ports

        self.host_service.update_ports(ports_by_ip, scan_type)
        return ports_by_ip

    def scan_target_ip(self, target_ip: str, scan_type: PortScanType) -> List[Port] | None:
        try:
            scan_result = self.nmap.scan(target_ip, scan_type.value)
        except nmap.PortScannerError as e:
            logging.error(f"An error occurred while scanning ports on {target_ip}: {e}")
            return None

        open_ports: List[Port] = []
        tcp_scan: Dict[int, Dict[str, Any]] = (
            scan_result['scan']
            .get(target_ip, {})
            .get('tcp', {})
        )

        for port, port_info in tcp_scan.items():
            if port_info.get('state') != 'open':
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