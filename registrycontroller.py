from typing import Optional
from fastapi import APIRouter, HTTPException
from dto.schemas import HeartbeatRequest, ServiceRegisterRequest
from manager import registrymanager as rm


router = APIRouter(prefix="/api/services", tags=["Service Registry"])


# ==========================================
# LIST & DISCOVER SERVICES
# ==========================================
@router.get("")
def list_all_services():
    services = rm.list_services()
    return {"status": 200, "message": "Services fetched successfully", "data": services}


@router.get("/discover")
def discover_services(service_name: Optional[str] = None):
    healthy = rm.discover_healthy(service_name)
    return {
        "status": 200,
        "message": "Healthy instances discovered",
        "data": healthy,
    }


# ==========================================
# REGISTER, HEARTBEAT & DEREGISTER
# ==========================================
@router.post("/register")
def register_instance(payload: ServiceRegisterRequest):
    svc = rm.register_service(
        name=payload.name,
        instance=payload.instance,
        version=payload.version,
        port=payload.port,
        availability_zone=payload.availability_zone,
    )
    return {"status": 200, "message": "Service instance registered", "data": svc}


@router.post("/heartbeat")
def send_heartbeat(payload: HeartbeatRequest):
    svc = rm.record_heartbeat(payload.instance)
    if svc is None:
        raise HTTPException(status_code=404, detail="Instance not found")
    return {"status": 200, "message": "Heartbeat recorded", "data": svc}


@router.delete("/{instance}")
def deregister_instance(instance: str):
    removed = rm.deregister_service(instance)
    if not removed:
        raise HTTPException(status_code=404, detail="Instance not found")
    return {"status": 200, "message": "Service instance deregistered", "data": {"instance": instance}}
