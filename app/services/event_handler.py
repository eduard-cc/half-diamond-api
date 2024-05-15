import logging
import json
from typing import List
from fastapi import WebSocket
from utils.date_time_encoder import DateTimeEncoder
from services.event import Event

class EventHandler:
    def __init__(self, websocket: WebSocket | None = None):
        self.websocket: WebSocket | None = websocket
        self.events: List[Event] = []

    async def dispatch(self, event: Event):
        self.events.append(event)
        if self.websocket:
            logging.info(f"Dispatching event: {event.type} for host: {event.data.mac}")
            data = json.dumps(event.model_dump(), cls=DateTimeEncoder)
            await self.websocket.send_text(data)

    def get_events(self) -> List[Event]:
        return self.events