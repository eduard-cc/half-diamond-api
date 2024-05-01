from fastapi import APIRouter, WebSocket, BackgroundTasks
from services.monitor import Monitor
from models.host import Host
from typing import List

monitor_router = APIRouter()
monitor = Monitor('host_cache.json')

@monitor_router.websocket_route("/ws")
async def websocket_endpoint_monitor(websocket: WebSocket):
    await websocket.accept()
    monitor.websocket = websocket
    monitor.host_cache.websocket = websocket
    while True:
        await websocket.receive_text()

@monitor_router.get("/hosts", response_model=List[Host])
def get_hosts():
    return monitor.host_cache.load()

@monitor_router.get("/status")
def get_monitor_status():
    return {"running": monitor.is_running()}

@monitor_router.post("/start")
async def start_monitor(background_tasks: BackgroundTasks):
    if monitor.websocket is not None:
        background_tasks.add_task(monitor.start)
        return {"message": "Monitor started"}
    else:
        return {"message": "No active websocket connection"}

@monitor_router.post("/stop")
async def stop_monitor():
    monitor.stop()
    return {"message": "Monitor stopped"}