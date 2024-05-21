from fastapi import APIRouter, HTTPException, BackgroundTasks
from core.host.model import Host
from typing import List
from core.session_setup import session

monitor_router = APIRouter()

@monitor_router.get("/hosts", response_model=List[Host])
def get_hosts():
    return session.host_service.get_hosts()

@monitor_router.get("/status")
def get_monitor_status():
    return {"running": session.monitor.is_running}

@monitor_router.post("/start")
async def start_monitor(background_tasks: BackgroundTasks):
    try:
        background_tasks.add_task(session.monitor.start)
        return {"message": "Monitor started"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@monitor_router.post("/stop")
async def stop_monitor():
    try:
        session.monitor.stop()
        return {"message": "Monitor stopped"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))