from fastapi import APIRouter, BackgroundTasks
from services.probe import Probe

probe_router = APIRouter()
probe = Probe()

@probe_router.get("/status")
def get_probe_status():
    return {"running": probe.is_running()}

@probe_router.post("/start")
async def start_probe(background_tasks: BackgroundTasks):
    background_tasks.add_task(probe.start)
    return {"message": "Probe started"}

@probe_router.post("/stop")
async def stop_probe():
    probe.stop()
    return {"message": "Probe stopped"}