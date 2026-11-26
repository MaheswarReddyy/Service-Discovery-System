import csv
import os
import random
from datetime import datetime, timedelta


# ==========================================
# SYNTHETIC STARTER DATASET GENERATOR
# ==========================================
def generate_pack(out_dir: str, seed: int = 20260101) -> None:
    rng = random.Random(seed)
    os.makedirs(out_dir, exist_ok=True)
    start_ts = datetime(2026, 11, 20, 8, 0, 0)

    services = [
        ("api-gateway", 8080),
        ("user-service", 8081),
        ("order-service", 8083),
        ("payment-service", 8085),
        ("inventory-service", 8087),
        ("notification-service", 8089),
    ]
    zones = ["az-1", "az-2", "az-3"]

    # 1. service_inventory.csv (24 rows)
    inventory_rows = []
    for svc, base_port in services:
        for idx in range(1, 5):
            inventory_rows.append(
                [
                    svc,
                    f"{svc}-{idx:02d}",
                    base_port + idx,
                    zones[(idx - 1) % len(zones)],
                    f"v1.{idx}",
                    "HTTP/REST",
                    "/health",
                ]
            )
    with open(os.path.join(out_dir, "service_inventory.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["service_name", "instance_id", "port", "availability_zone", "release_version", "protocol", "health_check_path"])
        w.writerows(inventory_rows)

    # 2. service_registry_events.csv (600 rows)
    ev_types = ["REGISTER", "HEARTBEAT", "HEALTHY", "UNHEALTHY", "DEREGISTER"]
    with open(os.path.join(out_dir, "service_registry_events.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["event_id", "timestamp", "service_name", "instance_id", "event_type", "healthy_after_event", "availability_zone"])
        for i in range(1, 601):
            row = rng.choice(inventory_rows)
            etype = rng.choices(ev_types, weights=[10, 55, 15, 12, 8])[0]
            healthy_after = 0 if etype in ("UNHEALTHY", "DEREGISTER") else 1
            ts = (start_ts + timedelta(seconds=i * 30)).isoformat()
            w.writerow([f"reg-{i:04d}", ts, row[0], row[1], etype, healthy_after, row[3]])

    # 3. dynamic_config_events.csv (300 rows)
    params = ["endpoint", "timeout_ms", "retry_count", "feature_flag"]
    statuses = ["APPLIED", "DELAYED", "FAILED", "STALE"]
    with open(os.path.join(out_dir, "dynamic_config_events.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["config_event_id", "timestamp", "service_name", "config_id", "version", "parameter", "value", "delivery_status", "propagation_delay_ms"])
        for i in range(1, 301):
            svc = rng.choice(services)[0]
            param = rng.choice(params)
            status = rng.choices(statuses, weights=[77, 11, 7, 5])[0]
            delay = round(rng.uniform(200, 2500), 1)
            ts = (start_ts + timedelta(seconds=i * 120)).isoformat()
            w.writerow([f"cfg-{i:04d}", ts, svc, f"cfg-{svc}", f"v{(i // 20) + 1}", param, str(rng.randint(1, 5000)), status, delay])

    # 4. fault_injection_events.csv (150 rows)
    fault_types = ["NETWORK_PARTITION", "CONFIG_SERVER_UNAVAILABLE", "CASCADING_FAILURE", "INSTANCE_CRASH", "HIGH_CPU"]
    rec_statuses = ["RECOVERED", "DEGRADED", "UNRECOVERED"]
    with open(os.path.join(out_dir, "fault_injection_events.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["fault_id", "start_timestamp", "fault_type", "affected_service", "duration_seconds", "recovery_status", "affected_instances"])
        for i in range(1, 151):
            svc = rng.choice(services)[0]
            ftype = rng.choice(fault_types)
            rstat = rng.choices(rec_statuses, weights=[79, 14, 7])[0]
            ts = (start_ts + timedelta(seconds=i * 238)).isoformat()
            w.writerow([f"flt-{i:04d}", ts, ftype, svc, rng.randint(5, 120), rstat, f"{svc}-01"])

    # 5. request_telemetry.csv (1000 rows)
    with open(os.path.join(out_dir, "request_telemetry.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["request_id", "timestamp", "target_service", "target_instance", "latency_ms", "result", "churn_active", "network_partition", "routed_to_dead_instance", "used_stale_config", "config_version_seen"])
        for i in range(1, 1001):
            row = rng.choice(inventory_rows)
            churn = 1 if rng.random() < 0.14 else 0
            part = 1 if rng.random() < 0.07 else 0
            dead = 1 if (churn and rng.random() < 0.41) else 0
            stale = 1 if (not dead and rng.random() < 0.03) else 0
            err = 1 if (dead or stale or (part and rng.random() < 0.45) or rng.random() < 0.03) else 0
            lat = round(rng.uniform(45, 195), 1) if not err else round(rng.uniform(220, 480), 1)
            ts = (start_ts + timedelta(seconds=i * 15)).isoformat()
            w.writerow([f"req-{i:04d}", ts, row[0], row[1], lat, "ERROR" if err else "SUCCESS", churn, part, dead, stale, f"v{rng.randint(1, 15)}"])


if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    generate_pack(here)
    print("Generated 5 dataset CSVs in", here)
