from typing import List
from fastapi import APIRouter, HTTPException, BackgroundTasks
from services.session import session

arp_spoof_router = APIRouter()

@arp_spoof_router.get("/status")
def get_arp_spoof_status():
    return {"running": session.arp_spoof.is_running}

@arp_spoof_router.post("/start")
async def start_arp_spoof(background_tasks: BackgroundTasks,
                          target_ips: List[str]):
    try:
        background_tasks.add_task(session.arp_spoof.start, target_ips)
        return {"message": "ARP spoof started"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@arp_spoof_router.post("/stop")
async def stop_arp_spoof():
    try:
        session.arp_spoof.stop()
        return {"message": "ARP spoof stopped"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))