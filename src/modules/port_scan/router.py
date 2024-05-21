from typing import Dict, List
from fastapi import APIRouter, Query
from modules.port_scan.model import PortScanType
from modules.port_scan.service import PortScan
from core.host.model import Port
from core.session_setup import session

port_scan_router = APIRouter()

@port_scan_router.patch("/ports", response_model=Dict[str, List[Port]])
def scan_ports(target_ips: List[str],
               type: PortScanType = Query(default = PortScanType.SYN)):
    port_scanner = PortScan(session.host_service)
    return port_scanner.scan_ports(target_ips, type)