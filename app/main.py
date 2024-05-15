import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers.monitor_router import monitor_router
from routers.probe_router import probe_router
from routers.port_scan_router import port_scan_router
from routers.os_detection_router import os_detection_router
from routers.event_router import event_router

app = FastAPI()

logging.basicConfig(level=logging.INFO)

origins = [
    "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(monitor_router, prefix="/monitor")
app.include_router(probe_router, prefix="/probe")
app.include_router(event_router, prefix="/events")
app.include_router(port_scan_router)
app.include_router(os_detection_router)