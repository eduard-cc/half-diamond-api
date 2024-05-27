from typing import Dict, List
from fastapi import APIRouter
from modules.os_detect.service import OsDetect
from core.session_setup import session

os_detection_router = APIRouter()

@os_detection_router.patch("/os",
                           response_model=Dict[str, str],
                           summary="Scan OS",
                           description="""
                           Detect the Operating System of the target IPs.
                           """,
                           tags=["Scan"])
def scan_os(target_ips: List[str]):
    os_detector = OsDetect(session.host_service)
    return os_detector.detect_os(target_ips)