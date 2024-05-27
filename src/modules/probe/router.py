from fastapi import APIRouter, BackgroundTasks, HTTPException
from core.session_setup import session

probe_router = APIRouter()

@probe_router.get("/status",
                  summary="Get Probe status",
                  description="Get the status of the Probe module.",
                  tags=["Probe"])
def get_probe_status():
    return {"running": session.probe.is_running}

@probe_router.post("/start",
                   summary="Start Probe",
                   description="""
                   Start actively probing the network by periodically sending
                   ARP requests to all the IPs in the subnet.
                   """,
                   tags=["Probe"])
async def start_probe(background_tasks: BackgroundTasks):
    try:
        background_tasks.add_task(session.probe.start)
        return {"message": "Probe started"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@probe_router.post("/stop",
                   summary="Stop Probe",
                   description="""
                   Stop actively probing the network for active hosts.
                   """,
                   tags=["Probe"])
async def stop_probe():
    try:
        session.probe.stop()
        return {"message": "Probe stopped"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))