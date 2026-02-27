from pydantic import BaseModel
from datetime import datetime

class VaultPadlockMetrics(BaseModel):
    id: str
    cpu: str
    temperature: str
    timestamp: datetime

class VaultPadlockStatus(BaseModel):
    id: str
    state: str
    last_unlock: str | None
    battery: str
    error: str | None
    timestamp: datetime

class VaultPadlockEvents(BaseModel):
    id: str
    event: str
    result: str
    timestamp: datetime

class ControlComputerLock(BaseModel):
    id: str
    lock_state: str
    reason: str
    timestamp: datetime
