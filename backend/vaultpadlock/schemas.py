from pydantic import BaseModel
from datetime import datetime
from enum import StrEnum

class TopicEndpoints(StrEnum):
    events: str = "events"
    status: str = "status"
    metrics: str = "metrics"

class VaultPadlockMetrics(BaseModel):
    id: str
    cpu: str
    temperature: str
    timestamp: datetime

    model_config = {"extra": "ignore"}

class VaultPadlockStatus(BaseModel):
    id: str
    state: str
    last_unlock: str | None
    battery: str
    error: str | None
    timestamp: datetime

    model_config = {"extra": "ignore"}

class VaultPadlockEvents(BaseModel):
    id: str
    event: str
    result: str
    timestamp: datetime

    model_config = {"extra": "ignore"}

class ControlComputerLock(BaseModel):
    id: str
    lock_state: str
    reason: str
    timestamp: datetime

    model_config = {"extra": "ignore"}
