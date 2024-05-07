from typing import Dict, List
from fastapi import APIRouter
from services.os_detection import OSDetection
from services.session import session

os_detection_router = APIRouter()

@os_detection_router.patch("/os", response_model=Dict[str, str])
def scan_os(target_ips: List[str]):
    os_detector = OSDetection(session.host_service)
    return os_detector.detect_os(target_ips)