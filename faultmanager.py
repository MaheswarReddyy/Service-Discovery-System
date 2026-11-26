import random
import time
from typing import Any, Dict, Optional
from repository import staterepository as sr


# ==========================================
# FAULT INJECTION & RECOVERY ENGINE
# ==========================================
def inject_fault(
    fault_type: str,
    target_instance: Optional[str] = None,
    target_service: Optional[str] = None,
) -> Dict[str, Any]:
    state = sr.load_state()
    now = time.time()
    affected = []

    if fault_type == "INSTANCE_CRASH" and target_instance:
        for svc in state["services"]:
            if svc["instance"] == target_instance:
                svc["status"] = "Failed"
                affected.append(svc["instance"])

    elif fault_type == "NETWORK_PARTITION":
        state["partition_active"] = True
        for svc in state["services"]:
            if svc["availability_zone"] == "az-2":
                svc["status"] = "Failed"
                affected.append(svc["instance"])

    elif fault_type == "STALE_CONFIG":
        # Simulate An Instance Falling Behind On Config Version
        for svc in state["services"]:
            if (target_instance and svc["instance"] == target_instance) or (
                not target_instance and svc["status"] == "Healthy"
            ):
                svc["config_version"] = max(0, state["config"]["version"] - 1)
                affected.append(svc["instance"])
                if not target_instance:
                    break

    elif fault_type == "CASCADING_FAILURE":
        for svc in state["services"]:
            if target_service and svc["name"] == target_service:
                svc["status"] = "Failed"
                affected.append(svc["instance"])

    event = {
        "id": f"fault-{len(state['fault_log']) + 1:03d}",
        "fault_type": fault_type,
        "affected_instances": affected,
        "timestamp": now,
        "recovery_status": "ACTIVE",
    }
    state["fault_log"].append(event)
    sr.save_state(state)
    return event


def recover_instance(instance: str) -> Optional[Dict[str, Any]]:
    state = sr.load_state()
    now = time.time()
    latest_cfg = state["config"]["version"]
    recovered = None

    for svc in state["services"]:
        if svc["instance"] == instance:
            svc["status"] = "Healthy"
            svc["config_version"] = latest_cfg
            svc["last_heartbeat"] = now
            recovered = svc
            break

    if recovered is None:
        return None

    # Mark Matching Active Faults As Recovered If No Failed Instances Remain
    if all(s["status"] == "Healthy" for s in state["services"]):
        state["partition_active"] = False
        for evt in state["fault_log"]:
            if evt["recovery_status"] == "ACTIVE":
                evt["recovery_status"] = "RECOVERED"

    sr.save_state(state)
    return recovered


def recover_all() -> Dict[str, Any]:
    state = sr.load_state()
    now = time.time()
    latest_cfg = state["config"]["version"]

    for svc in state["services"]:
        svc["status"] = "Healthy"
        svc["config_version"] = latest_cfg
        svc["last_heartbeat"] = now

    state["partition_active"] = False
    for evt in state["fault_log"]:
        if evt["recovery_status"] == "ACTIVE":
            evt["recovery_status"] = "RECOVERED"

    sr.save_state(state)
    return {"recovered_count": len(state["services"]), "config_version": latest_cfg}


# ==========================================
# TELEMETRY & KPI SUMMARY
# ==========================================
def get_monitoring_metrics(refresh: bool = False) -> Dict[str, Any]:
    state = sr.load_state()
    services = state["services"]
    total = len(services)
    healthy = sum(1 for s in services if s["status"] == "Healthy")
    failed = total - healthy
    latest_cfg = state["config"]["version"]
    consistent = sum(1 for s in services if s.get("config_version", 0) == latest_cfg)

    if refresh:
        base_err = 0.12 if failed == 0 else round(min(15.0, (failed / max(1, total)) * 12.5), 2)
        state["telemetry"] = {
            "uptime": round(99.90 + random.uniform(0.0, 0.09), 2) if failed == 0 else round(98.5 + random.uniform(0.0, 1.0), 2),
            "requestRate": random.randint(1120, 1480),
            "responseTime": random.randint(115, 185) if failed == 0 else random.randint(180, 290),
            "errorRate": base_err,
        }
        sr.save_state(state)

    return {
        **state["telemetry"],
        "totalInstances": total,
        "healthyInstances": healthy,
        "failedInstances": failed,
        "configVersion": latest_cfg,
        "configConsistentInstances": consistent,
        "partitionActive": state.get("partition_active", False),
        "faultLogCount": len(state["fault_log"]),
    }
