from fastapi import APIRouter, HTTPException
from dto.schemas import FaultInjectRequest
from manager import faultmanager as fm
from repository import staterepository as sr


router = APIRouter(prefix="/api", tags=["Faults & Monitoring"])


# ==========================================
# FAULT INJECTION & RECOVERY ENDPOINTS
# ==========================================
@router.post("/faults/inject")
def inject_fault_endpoint(payload: FaultInjectRequest):
    evt = fm.inject_fault(
        fault_type=payload.fault_type,
        target_instance=payload.target_instance,
        target_service=payload.target_service,
    )
    return {"status": 200, "message": "Fault injected", "data": evt}


@router.post("/faults/recover/{instance}")
def recover_instance_endpoint(instance: str):
    svc = fm.recover_instance(instance)
    if svc is None:
        raise HTTPException(status_code=404, detail="Instance not found")
    return {
        "status": 200,
        "message": f"{instance} has recovered and is available again.",
        "data": svc,
    }


@router.post("/faults/recover-all")
def recover_all_endpoint():
    res = fm.recover_all()
    return {"status": 200, "message": "All instances recovered", "data": res}


@router.get("/faults/log")
def get_fault_log_endpoint():
    return {"status": 200, "message": "Fault log fetched", "data": sr.get_fault_log()}


# ==========================================
# MONITORING & TELEMETRY ENDPOINT
# ==========================================
@router.get("/monitoring")
def get_monitoring_endpoint(refresh: bool = False):
    metrics = fm.get_monitoring_metrics(refresh=refresh)
    return {"status": 200, "message": "Monitoring metrics fetched", "data": metrics}
