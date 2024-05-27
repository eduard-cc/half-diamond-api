from typing import List
from fastapi import APIRouter, HTTPException, BackgroundTasks
from core.session_setup import session

arp_spoof_router = APIRouter()

@arp_spoof_router.get("/status",
                      summary="Get ARP Spoof status",
                      description="""
                      Get the status of the ARP spoof module and the current
                      target IPs if running.
                      """,
                      tags=["ARP Spoof"])
def get_arp_spoof_status():
    return {
        "running": session.arp_spoof.is_running,
        "targets": session.arp_spoof.target_ips
    }

@arp_spoof_router.post("/start",
                       summary="Start ARP Spoof",
                       description="""
                       Start sending spoofed ARP packets to the targets.
                       """,
                       tags=["ARP Spoof"])
async def start_arp_spoof(background_tasks: BackgroundTasks,
                          target_ips: List[str]):
    try:
        background_tasks.add_task(session.arp_spoof.start, target_ips)
        return {"message": "ARP spoof started"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@arp_spoof_router.post("/stop",
                       summary="Stop ARP Spoof",
                       description="""
                       Stop sending spoofed packets and restore
                       the ARP tables of the targets.
                       """,
                       tags=["ARP Spoof"])
async def stop_arp_spoof():
    try:
        await session.arp_spoof.stop()
        return {"message": "ARP spoof stopped"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))