import time
from typing import Any, Dict
from repository import staterepository as sr


# ==========================================
# DYNAMIC CONFIGURATION MANAGEMENT
# ==========================================
def get_current_config() -> Dict[str, Any]:
    return sr.get_config()


def publish_config(
    request_timeout: int,
    max_retries: int,
    health_check_interval: int,
    load_balancing: str,
) -> Dict[str, Any]:
    state = sr.load_state()
    cfg = state["config"]
    next_version = int(cfg.get("version", 1)) + 1
    now = time.time()

    # Update Canonical Config Version
    cfg["version"] = next_version
    cfg["requestTimeout"] = request_timeout
    cfg["maxRetries"] = max_retries
    cfg["healthCheckInterval"] = health_check_interval
    cfg["loadBalancing"] = load_balancing
    cfg["updatedAt"] = now

    # Propagate Latest Config To Healthy Instances (Unless Partitioned)
    if not state.get("partition_active", False):
        for svc in state["services"]:
            if svc["status"] == "Healthy":
                svc["config_version"] = next_version

    sr.save_state(state)
    return cfg


def reconcile_config_versions() -> int:
    state = sr.load_state()
    latest = state["config"]["version"]
    updated = 0
    for svc in state["services"]:
        if svc["status"] == "Healthy" and svc.get("config_version", 0) < latest:
            svc["config_version"] = latest
            updated += 1
    if updated > 0:
        sr.save_state(state)
    return updated
