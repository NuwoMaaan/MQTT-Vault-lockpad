from pydantic import BaseModel
from datetime import datetime

class ControlComputerLock(BaseModel):
    id: str
    lock_state: str
    reason: str
    timestamp: datetime

    
    