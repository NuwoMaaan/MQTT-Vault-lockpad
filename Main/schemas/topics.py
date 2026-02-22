
from pydantic import BaseModel

class Topics(BaseModel):
    event: str = "<103996982>/padlock/event" # device -> broker -> control
    status: str = "<103996982>/padlock/status"
    metrics: str = "<103996982>/padlock/metrics"
    control: str = "<103996982>/padlock/control" # control -> broker -> device

TOPICS = Topics()