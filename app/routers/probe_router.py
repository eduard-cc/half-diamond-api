from fastapi import APIRouter, BackgroundTasks, HTTPException
from services.session import session

probe_router = APIRouter()

@probe_router.get("/status")
def get_probe_status():
    return {"running": session.probe.is_running()}

@probe_router.post("/start")
async def start_probe(background_tasks: BackgroundTasks):
    try:
        background_tasks.add_task(session.probe.start)
        return {"message": "Probe started"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@probe_router.post("/stop")
async def stop_probe():
    try:
        session.probe.stop()
        return {"message": "Probe stopped"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))