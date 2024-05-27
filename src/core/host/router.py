from fastapi import APIRouter
from core.host.model import Host
from typing import List
from core.session_setup import session

host_router = APIRouter()

@host_router.get("/",
                 response_model=List[Host],
                 summary="Get all hosts",
                 description="Get all hosts from the current session.",
                 tags=["Hosts"])
def get_hosts():
    return session.host_service.get_hosts()