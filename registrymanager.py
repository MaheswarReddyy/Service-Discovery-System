import time
from typing import Any, Dict, List, Optional
from repository import staterepository as sr


# ==========================================
# LEASE & CHURN EVICTION HELPERS
# ==========================================
def evict_expired_instances(lease_ttl_seconds: Optional[float] = None) -> int:
    state = sr.load_state()
    ttl = lease_ttl_seconds or max(15.0, float(state["config"]["healthCheckInterval"]) * 3.0)
    now = time.time()
    evicted = 0

    for svc in state["services"]:
        if svc["status"] == "Healthy" and (now - svc.get("last_heartbeat", now)) > ttl:
            svc["status"] = "Failed"
            evicted += 1

    if evicted > 0:
        sr.save_state(state)
    return evicted


# ==========================================
# SERVICE REGISTRATION & DISCOVERY
# ==========================================
def list_services() -> List[Dict[str, Any]]:
    state = sr.load_state()
    return state["services"]


def register_service(
    name: str,
    instance: str,
    version: str,
    port: int,
    availability_zone: str,
) -> Dict[str, Any]:
    state = sr.load_state()
    now = time.time()
    current_cfg_ver = state["config"]["version"]

    # Update Existing Instance If Present
    for svc in state["services"]:
        if svc["instance"] == instance:
            svc["name"] = name
            svc["version"] = version
            svc["port"] = port
            svc["availability_zone"] = availability_zone
            svc["status"] = "Healthy"
            svc["config_version"] = current_cfg_ver
            svc["last_heartbeat"] = now
            sr.save_state(state)
            return svc

    # Insert New Service Instance
    new_svc = {
        "name": name,
        "instance": instance,
        "status": "Healthy",
        "version": version,
        "port": port,
        "availability_zone": availability_zone,
        "config_version": current_cfg_ver,
        "last_heartbeat": now,
    }
    state["services"].append(new_svc)
    sr.save_state(state)
    return new_svc


def record_heartbeat(instance: str) -> Optional[Dict[str, Any]]:
    state = sr.load_state()
    now = time.time()
    current_cfg_ver = state["config"]["version"]

    for svc in state["services"]:
        if svc["instance"] == instance:
            svc["last_heartbeat"] = now
            svc["status"] = "Healthy"
            svc["config_version"] = current_cfg_ver
            sr.save_state(state)
            return svc
    return None


def deregister_service(instance: str) -> bool:
    state = sr.load_state()
    before = len(state["services"])
    state["services"] = [s for s in state["services"] if s["instance"] != instance]
    if len(state["services"]) == before:
        return False
    sr.save_state(state)
    return True


def discover_healthy(service_name: Optional[str] = None) -> List[Dict[str, Any]]:
    # Never Route To Failed Or Stale-Config Instances
    state = sr.load_state()
    current_ver = state["config"]["version"]
    results = []
    for svc in state["services"]:
        if svc["status"] != "Healthy":
            continue
        if svc.get("config_version", 0) < current_ver:
            continue
        if service_name and svc["name"].lower() != service_name.lower():
            continue
        results.append(svc)
    return results
