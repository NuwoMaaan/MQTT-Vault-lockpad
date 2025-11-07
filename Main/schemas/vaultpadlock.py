from pydantic import BaseModel
from datetime import datetime

class VaultPadlockMetrics(BaseModel):
    id: str
    cpu: str
    login_attempts: int
    netstats: dict[str, str]
    timestamp: datetime

class VaultPadlockStatus(BaseModel):
    id: str
    state: str
    error: str | None
    timestamp: datetime
