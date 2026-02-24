
from pydantic import BaseModel

class Topics(BaseModel):
    event: str = "vault/padlock/event" # device -> broker -> control
    status: str = "vault/padlock/status"
    metrics: str = "vault/padlock/metrics"
    control: str = "vault/padlock/control" # control -> broker -> device

TOPICS = Topics()