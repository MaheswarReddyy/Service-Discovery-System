# CLOUD-26: Service Discovery and Dynamic Configuration Surviving Churn and Partial Failure

**Team No.:** C2C 88 | **Portal Use-Case ID:** CLOUD-26  
**Cluster:** Cloud & Edge Computing (KL University Capstone Project)  
**Team Members:** Arumalla Jahnavi (2300030046), Panchireddi Joshiram (2300030507), Gogula Naga Maheshwar Reddy (2300030990)  
**Faculty Guide:** Dr. B. Namashivayam, Associate Professor, CSE

---

## Project Structure

```
ServiceDiscoveryProject/
├── backend/                 # Python 3.12+ / FastAPI Control Plane (3-tier functional architecture)
│   ├── config/              # CORS & application settings
│   ├── controller/          # Thin APIRouter endpoints (/api/services, /api/config, /api/faults, /api/monitoring)
│   ├── dto/                 # Pydantic v2 request/response schemas
│   ├── manager/             # Registry, Dynamic Config, and Fault/Recovery business logic
│   ├── repository/          # Durable JSON checkpoint state persistence
│   ├── tests/               # Smoke & negative tests (NT-1, NT-2)
│   ├── main.py              # FastAPI entrypoint
│   └── requirements.txt
├── frontend/                # React 19 + Vite Operational Dashboard
│   ├── src/
│   │   ├── App.jsx          # Dashboard, Service Registry, Dynamic Config, Failure Simulation, Monitoring
│   │   ├── App.css
│   │   └── main.jsx
│   └── package.json
├── dataset/                 # Synthetic Starter Pack & KPI Oracle
│   ├── generate_dataset.py  # Generates the 5 starter CSVs (seed 20260101)
│   ├── analyze_pack.py      # Computes KPI-1..KPI-6 with Wilson & bootstrap 95% intervals
│   ├── *.csv                # request_telemetry, service_registry_events, dynamic_config_events, fault_injection_events, service_inventory
│   └── results.json         # Evaluated KPI oracle output
└── README.md
```

---

## Quick Start

### 1. Start the FastAPI Backend (Port 8000)
```powershell
cd backend
pip install -r requirements.txt
uvicorn main:app --host 127.0.0.1 --port 8000
```

### 2. Start the React Frontend (Port 5173)
```powershell
cd frontend
npm install
npm run dev
```

### 3. Run Smoke & Negative Tests
```powershell
cd backend
python tests/test_smoke.py
```

### 4. Generate & Analyze Starter Dataset
```powershell
cd dataset
python generate_dataset.py
python analyze_pack.py
```
