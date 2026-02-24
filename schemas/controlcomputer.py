from pydantic import BaseModel


class ControlComputerLock(BaseModel):
    id: str
    lock_state: str
    reason: str

    
    