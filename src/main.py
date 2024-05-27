from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from modules.monitor.router import monitor_router
from modules.probe.router import probe_router
from modules.arp_spoof.router import arp_spoof_router
from modules.port_scan.router import port_scan_router
from modules.os_detect.router import os_detection_router
from core.host.router import host_router
from core.event.router import event_router

app = FastAPI(
    title="netpick API",
    description="A pen testing toolkit for network recon and MITM attacks.",
    version="1.0",
)

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
app.include_router(host_router, prefix="/hosts")
app.include_router(probe_router, prefix="/probe")
app.include_router(arp_spoof_router, prefix="/arp-spoof")
app.include_router(event_router, prefix="/events")
app.include_router(port_scan_router)
app.include_router(os_detection_router)