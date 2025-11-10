from pydantic import BaseModel


class ControlComputerKeepAlive(BaseModel):
    id: str
    keepalive: str

class ControlComputerLock(BaseModel):
    id: str
    lock_state: str
    