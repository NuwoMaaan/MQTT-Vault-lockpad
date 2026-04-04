from pydantic import BaseModel
from datetime import datetime


class BleData(BaseModel):
    id: str
    UUID: str
    token: str
    localname: str
    timestamp: datetime

    model_config = {"extra": "ignore"}