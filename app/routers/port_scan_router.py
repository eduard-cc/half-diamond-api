from typing import Dict, List
from fastapi import APIRouter
from models.host import Port
from services.port_scan import PortScan

port_scan_router = APIRouter()
port_scanner = PortScan()

@port_scan_router.patch("/ports", response_model=Dict[str, List[Port]])
def scan_ports(target_ips: List[str]):
    return port_scanner.scan_ports(target_ips)