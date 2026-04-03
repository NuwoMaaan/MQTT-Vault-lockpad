from pydantic import BaseModel
from datetime import datetime
from enum import StrEnum


class BleToken(BaseModel):
    id: str
    token: str
    UUID: str
    local_name: str
    timestamp: datetime

    model_config = {"extra": "ignore"}

class TokenRequest(BaseModel):
    id: str
    request: str
    timestamp: datetime

    model_config = {"extra": "ignore"}

# class StoreToken(BaseModel):
#     id: str
#     token: str
#     UUID: str
#     localname: str
#     timestamp: datetime