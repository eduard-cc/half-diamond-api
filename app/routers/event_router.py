from typing import List
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from services.event import Event
from services.session import session

event_router = APIRouter()

async def websocket_endpoint(websocket: WebSocket):
    try:
        await websocket.accept()
        session.event_handler.websocket = websocket
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        session.event_handler.websocket = None
    except Exception:
        await websocket.close()

event_router.add_route("/ws", websocket_endpoint, methods=["GET"], include_in_schema=False)

@event_router.get("/", response_model=List[Event])
def get_hosts():
    return session.event_handler.get_events()