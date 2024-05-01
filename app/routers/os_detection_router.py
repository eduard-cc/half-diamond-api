from typing import Dict, List
from fastapi import APIRouter
from services.os_detection import OSDetection

os_detection_router = APIRouter()
os_detector = OSDetection()

@os_detection_router.patch("/os", response_model=Dict[str, str])
def scan_os(target_ips: List[str]):
    return os_detector.detect_os(target_ips)