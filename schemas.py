from typing import Optional
from pydantic import BaseModel, Field


# ==========================================
# SERVICE REGISTRY SCHEMAS
# ==========================================
class ServiceRegisterRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=80)
    instance: str = Field(..., min_length=1, max_length=80)
    version: str = Field(default="v1.0", max_length=32)
    port: int = Field(default=8080, ge=1, le=65535)
    availability_zone: str = Field(default="az-1", max_length=32)


class HeartbeatRequest(BaseModel):
    instance: str = Field(..., min_length=1, max_length=80)


# ==========================================
# DYNAMIC CONFIGURATION SCHEMAS
# ==========================================
class ConfigUpdateRequest(BaseModel):
    requestTimeout: int = Field(..., ge=100, le=60000)
    maxRetries: int = Field(..., ge=0, le=10)
    healthCheckInterval: int = Field(..., ge=1, le=120)
    loadBalancing: str = Field(..., min_length=1, max_length=40)


# ==========================================
# FAULT INJECTION & RECOVERY SCHEMAS
# ==========================================
class FaultInjectRequest(BaseModel):
    fault_type: str = Field(
        default="INSTANCE_CRASH",
        description="INSTANCE_CRASH | NETWORK_PARTITION | STALE_CONFIG | CASCADING_FAILURE",
    )
    target_instance: Optional[str] = None
    target_service: Optional[str] = None
