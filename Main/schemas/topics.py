
from pydantic import BaseModel
    
class Topics(BaseModel):
    control: str = "<103996982>/padlock/control"
    status: str = "<103996982>/padlock/status"
    metrics: str = "<103996982>/padlock/metrics"
    lockout: str = "<103996982>/padlock/control/lockout"

TOPICS = Topics()