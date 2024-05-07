import logging
import json
from typing import Callable, Dict, List, Type
from fastapi import WebSocket
from utils.date_time_encoder import DateTimeEncoder
from services.event import Event

class EventHandler:
    def __init__(self, websocket: WebSocket | None = None):
        self.handlers: Dict[Type[Event], List[Callable[[Event], None]]] = {}
        self.websocket: WebSocket | None = websocket

    def register(self, event_class: Type[Event], handler: Callable[[Event], None]):
        if event_class not in self.handlers:
            self.handlers[event_class] = []
        self.handlers[event_class].append(handler)

    async def dispatch(self, event: Event):
        logging.info(f"Dispatching event: {event.type} for host: {event.data.mac}")
        for handler in self.handlers.get(type(event), []):
            await handler(event)
        if self.websocket:
            data = json.dumps(event.to_dict(), cls=DateTimeEncoder)
            await self.websocket.send_text(data)