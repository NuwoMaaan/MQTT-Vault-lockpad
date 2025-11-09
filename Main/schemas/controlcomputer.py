from pydantic import BaseModel


class ControlComputerKeepAlive(BaseModel):
    id: str
    keepalive: str
    