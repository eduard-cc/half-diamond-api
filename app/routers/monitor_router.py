from fastapi import APIRouter, HTTPException, WebSocket, BackgroundTasks
from services.monitor import Monitor
from models.host import Host
from typing import List

monitor_router = APIRouter()
monitor = Monitor()

@monitor_router.websocket_route("/ws")
async def websocket_endpoint_monitor(websocket: WebSocket):
    try:
        await websocket.accept()
        monitor.websocket = websocket
        monitor.host_cache.websocket = websocket
        while True:
            await websocket.receive_text()
    except Exception as e:
        await websocket.send_text(f"Error: {e}")
        await websocket.close()

@monitor_router.get("/hosts", response_model=List[Host])
def get_hosts():
    return monitor.host_cache.load()

@monitor_router.get("/status")
def get_monitor_status():
    return {"running": monitor.is_running()}

@monitor_router.post("/start")
async def start_monitor(background_tasks: BackgroundTasks):
    try:
        background_tasks.add_task(monitor.start)
        return {"message": "Monitor started"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@monitor_router.post("/stop")
async def stop_monitor():
    try:
        monitor.stop()
        return {"message": "Monitor stopped"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))