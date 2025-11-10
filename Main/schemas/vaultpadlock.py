from pydantic import BaseModel
from datetime import datetime

class VaultPadlockMetrics(BaseModel):
    id: str
    cpu: str
    temperature: str
    unlock_attempts: int
    netstats: dict[str, str]
    timestamp: datetime

class VaultPadlockStatus(BaseModel):
    id: str
    state: str
    last_unlock: str | None
    battery: str
    error: str | None
    timestamp: datetime
