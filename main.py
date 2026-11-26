from fastapi import FastAPI
from config import appconfig as ac
from controller import configcontroller as cc
from controller import faultcontroller as fc
from controller import registrycontroller as rc


# ==========================================
# FASTAPI APPLICATION ENTRYPOINT
# ==========================================
app = FastAPI(
    title="CLOUD-26 Service Discovery & Dynamic Configuration API",
    version="1.0.0",
)

ac.configure_cors(app)
app.include_router(rc.router)
app.include_router(cc.router)
app.include_router(fc.router)


@app.get("/health")
def health_check():
    return {"status": 200, "message": "Control plane healthy", "data": {"ok": True}}
