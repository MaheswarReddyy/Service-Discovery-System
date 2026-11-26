import os
import sys
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main import app  # noqa: E402

client = TestClient(app)


# ==========================================
# SMOKE & NEGATIVE TEST SUITE (NT-1..NT-5)
# ==========================================
def test_health_and_list():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["data"]["ok"] is True

    r2 = client.get("/api/services")
    assert r2.status_code == 200
    assert len(r2.json()["data"]) >= 7


def test_nt1_dead_instance_excluded_from_discovery():
    client.post("/api/faults/recover-all")
    r_inj = client.post(
        "/api/faults/inject",
        json={"fault_type": "INSTANCE_CRASH", "target_instance": "user-01"},
    )
    assert r_inj.status_code == 200

    r_disc = client.get("/api/services/discover", params={"service_name": "User Service"})
    instances = [s["instance"] for s in r_disc.json()["data"]]
    assert "user-01" not in instances
    assert "user-02" in instances

    r_rec = client.post("/api/faults/recover/user-01")
    assert r_rec.status_code == 200


def test_nt2_stale_config_excluded_and_reconciled():
    client.post("/api/faults/recover-all")
    r_cfg = client.put(
        "/api/config",
        json={
            "requestTimeout": 4500,
            "maxRetries": 4,
            "healthCheckInterval": 10,
            "loadBalancing": "Least Connections",
        },
    )
    assert r_cfg.status_code == 200

    r_stale = client.post(
        "/api/faults/inject",
        json={"fault_type": "STALE_CONFIG", "target_instance": "order-01"},
    )
    assert r_stale.status_code == 200

    r_disc = client.get("/api/services/discover", params={"service_name": "Order Service"})
    instances = [s["instance"] for s in r_disc.json()["data"]]
    assert "order-01" not in instances
    assert "order-02" in instances

    r_rec = client.post("/api/config/reconcile")
    assert r_rec.status_code == 200
    assert r_rec.json()["data"]["reconciled_instances"] >= 1


if __name__ == "__main__":
    test_health_and_list()
    test_nt1_dead_instance_excluded_from_discovery()
    test_nt2_stale_config_excluded_and_reconciled()
    print("ALL SMOKE AND NEGATIVE TESTS PASSED")
