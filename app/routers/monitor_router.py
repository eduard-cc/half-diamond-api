from fastapi import APIRouter, HTTPException, WebSocket, BackgroundTasks, WebSocketDisconnect
from models.host import Host
from typing import List
from services.session import session

monitor_router = APIRouter()

@monitor_router.websocket_route("/ws")
async def websocket_endpoint_monitor(websocket: WebSocket):
    try:
        await websocket.accept()
        session.event_handler.websocket = websocket
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect as e:
        print(f"WebSocket disconnected: {e}")
        session.event_handler.websocket = None
    except Exception as e:
        await websocket.send_text(f"Error: {e}")
        await websocket.close()

@monitor_router.get("/hosts", response_model=List[Host])
def get_hosts():
    return session.host_service.get_hosts()

@monitor_router.get("/status")
def get_monitor_status():
    return {"running": session.monitor.is_running()}

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