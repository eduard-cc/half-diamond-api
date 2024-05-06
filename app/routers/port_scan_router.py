from typing import Dict, List
from fastapi import APIRouter, Query
from services.port_scan_type import PortScanType
from models.host import Port
from services.port_scan import PortScan
from services.session import session

port_scan_router = APIRouter()

@port_scan_router.patch("/ports", response_model=Dict[str, List[Port]])
def scan_ports(target_ips: List[str], scan_type: PortScanType = Query(default = PortScanType.SYN)):
    port_scanner = PortScan(session.host_service)
    return port_scanner.scan_ports(target_ips, scan_type)