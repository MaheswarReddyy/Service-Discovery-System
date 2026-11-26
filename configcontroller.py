from fastapi import APIRouter
from dto.schemas import ConfigUpdateRequest
from manager import configmanager as cm


router = APIRouter(prefix="/api/config", tags=["Dynamic Configuration"])


# ==========================================
# GET & PUBLISH DYNAMIC CONFIGURATION
# ==========================================
@router.get("")
def fetch_config():
    cfg = cm.get_current_config()
    return {"status": 200, "message": "Configuration fetched successfully", "data": cfg}


@router.put("")
def update_config(payload: ConfigUpdateRequest):
    cfg = cm.publish_config(
        request_timeout=payload.requestTimeout,
        max_retries=payload.maxRetries,
        health_check_interval=payload.healthCheckInterval,
        load_balancing=payload.loadBalancing,
    )
    return {"status": 200, "message": "Configuration updated successfully!", "data": cfg}


@router.post("/reconcile")
def reconcile_configs():
    count = cm.reconcile_config_versions()
    return {
        "status": 200,
        "message": "Configuration reconciliation completed",
        "data": {"reconciled_instances": count},
    }
