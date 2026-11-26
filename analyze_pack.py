import hashlib
import json
import math
import os
import sys
import numpy as np
import pandas as pd


# ==========================================
# STATISTICAL INTERVAL HELPERS
# ==========================================
def wilson_interval(k: int, n: int, z: float = 1.96):
    if n == 0:
        return [0.0, 0.0]
    p = k / n
    denom = 1 + (z * z) / n
    center = (p + (z * z) / (2 * n)) / denom
    half = (z * math.sqrt((p * (1 - p) + (z * z) / (4 * n)) / n)) / denom
    return [round(max(0.0, center - half) * 100, 2), round(min(1.0, center + half) * 100, 2)]


def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


# ==========================================
# KPI ORACLE EVALUATION
# ==========================================
def analyze_dataset(data_dir: str, out_dir: str) -> dict:
    req = pd.read_csv(os.path.join(data_dir, "request_telemetry.csv"))
    cfg = pd.read_csv(os.path.join(data_dir, "dynamic_config_events.csv"))
    flt = pd.read_csv(os.path.join(data_dir, "fault_injection_events.csv"))

    churn_df = req[req["churn_active"] == 1]
    kpi1_k = int(((churn_df["result"] == "SUCCESS") & (churn_df["routed_to_dead_instance"] == 0)).sum())
    kpi1_n = int(len(churn_df))

    kpi2_k = int((cfg["delivery_status"] == "APPLIED").sum())
    kpi2_n = int(len(cfg))

    part_df = req[req["network_partition"] == 1]
    kpi3_k = int((part_df["result"] == "SUCCESS").sum())
    kpi3_n = int(len(part_df))

    kpi4_k = int((flt["recovery_status"] == "RECOVERED").sum())
    kpi4_n = int(len(flt))

    kpi5_k = int((req["result"] == "ERROR").sum())
    kpi5_n = int(len(req))

    lat = req["latency_ms"].to_numpy()
    rng = np.random.default_rng(20260101)
    boot_p95 = [np.percentile(rng.choice(lat, size=len(lat), replace=True), 95) for _ in range(2000)]

    files = [
        "request_telemetry.csv",
        "service_registry_events.csv",
        "dynamic_config_events.csv",
        "fault_injection_events.csv",
        "service_inventory.csv",
    ]
    hashes = {fn: sha256_file(os.path.join(data_dir, fn)) for fn in files}

    results = {
        "KPI-1_discovery_correctness_under_churn_pct": {
            "k": kpi1_k, "n": kpi1_n,
            "value": round((kpi1_k / kpi1_n) * 100, 2) if kpi1_n else 0.0,
            "ci95": wilson_interval(kpi1_k, kpi1_n),
        },
        "KPI-2_config_consistency_pct": {
            "k": kpi2_k, "n": kpi2_n,
            "value": round((kpi2_k / kpi2_n) * 100, 2) if kpi2_n else 0.0,
            "ci95": wilson_interval(kpi2_k, kpi2_n),
        },
        "KPI-3_availability_under_partition_pct": {
            "k": kpi3_k, "n": kpi3_n,
            "value": round((kpi3_k / kpi3_n) * 100, 2) if kpi3_n else 0.0,
            "ci95": wilson_interval(kpi3_k, kpi3_n),
        },
        "KPI-4_recovery_rate_pct": {
            "k": kpi4_k, "n": kpi4_n,
            "value": round((kpi4_k / kpi4_n) * 100, 2) if kpi4_n else 0.0,
            "ci95": wilson_interval(kpi4_k, kpi4_n),
        },
        "KPI-5_service_error_rate_pct": {
            "k": kpi5_k, "n": kpi5_n,
            "value": round((kpi5_k / kpi5_n) * 100, 2) if kpi5_n else 0.0,
            "ci95": wilson_interval(kpi5_k, kpi5_n),
        },
        "KPI-6_latency_ms": {
            "p50": round(float(np.percentile(lat, 50)), 2),
            "p95": round(float(np.percentile(lat, 95)), 2),
            "p99": round(float(np.percentile(lat, 99)), 2),
            "p95_ci95": [round(float(np.percentile(boot_p95, 2.5)), 2), round(float(np.percentile(boot_p95, 97.5)), 2)],
        },
        "sha256": hashes,
    }

    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, "results.json"), "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    return results


if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    d_dir = sys.argv[1] if len(sys.argv) > 1 else here
    o_dir = sys.argv[2] if len(sys.argv) > 2 else here
    res = analyze_dataset(d_dir, o_dir)
    print(json.dumps(res, indent=2))
