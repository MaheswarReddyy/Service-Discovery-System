import json
import os
import time
from typing import Any, Dict, List


# ==========================================
# STATE CHECKPOINT PATH & INITIAL SEED
# ==========================================
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHECKPOINT_PATH = os.path.join(BASE_DIR, "data", "checkpoint.json")

_STATE: Dict[str, Any] = {}


def _default_state() -> Dict[str, Any]:
    now = time.time()
    return {
        "config": {
            "version": 1,
            "requestTimeout": 5000,
            "maxRetries": 3,
            "healthCheckInterval": 10,
            "loadBalancing": "Round Robin",
            "updatedAt": now,
        },
        "services": [
            {
                "name": "User Service",
                "instance": "user-01",
                "status": "Healthy",
                "version": "v1.2",
                "port": 8081,
                "availability_zone": "az-1",
                "config_version": 1,
                "last_heartbeat": now,
            },
            {
                "name": "User Service",
                "instance": "user-02",
                "status": "Healthy",
                "version": "v1.2",
                "port": 8082,
                "availability_zone": "az-2",
                "config_version": 1,
                "last_heartbeat": now,
            },
            {
                "name": "Order Service",
                "instance": "order-01",
                "status": "Healthy",
                "version": "v2.1",
                "port": 8083,
                "availability_zone": "az-1",
                "config_version": 1,
                "last_heartbeat": now,
            },
            {
                "name": "Order Service",
                "instance": "order-02",
                "status": "Healthy",
                "version": "v2.1",
                "port": 8084,
                "availability_zone": "az-2",
                "config_version": 1,
                "last_heartbeat": now,
            },
            {
                "name": "Payment Service",
                "instance": "payment-01",
                "status": "Healthy",
                "version": "v1.5",
                "port": 8085,
                "availability_zone": "az-1",
                "config_version": 1,
                "last_heartbeat": now,
            },
            {
                "name": "Payment Service",
                "instance": "payment-02",
                "status": "Healthy",
                "version": "v1.5",
                "port": 8086,
                "availability_zone": "az-2",
                "config_version": 1,
                "last_heartbeat": now,
            },
            {
                "name": "Notification Service",
                "instance": "notification-01",
                "status": "Healthy",
                "version": "v1.1",
                "port": 8087,
                "availability_zone": "az-1",
                "config_version": 1,
                "last_heartbeat": now,
            },
        ],
        "partition_active": False,
        "fault_log": [],
        "telemetry": {
            "uptime": 99.98,
            "requestRate": 1248,
            "responseTime": 142,
            "errorRate": 0.12,
        },
    }


# ==========================================
# STATE LIFECYCLE FUNCTIONS
# ==========================================
def load_state() -> Dict[str, Any]:
    global _STATE
    if _STATE:
        return _STATE

    # Load Durable Checkpoint If Available
    if os.path.exists(CHECKPOINT_PATH):
        with open(CHECKPOINT_PATH, "r", encoding="utf-8") as f:
            _STATE = json.load(f)
        return _STATE

    _STATE = _default_state()
    save_state(_STATE)
    return _STATE


def save_state(state: Dict[str, Any]) -> None:
    os.makedirs(os.path.dirname(CHECKPOINT_PATH), exist_ok=True)
    with open(CHECKPOINT_PATH, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)


def get_services() -> List[Dict[str, Any]]:
    return load_state()["services"]


def get_config() -> Dict[str, Any]:
    return load_state()["config"]


def get_fault_log() -> List[Dict[str, Any]]:
    return load_state()["fault_log"]
