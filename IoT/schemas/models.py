from datetime import datetime
from pydantic import BaseModel

from schemas.padlock_enums import LockState, PadlockEvent, EventResult


class VaultPadlockMetrics(BaseModel):
    id: str
    cpu: str
    temperature: str
    timestamp: datetime


class VaultPadlockStatus(BaseModel):
    id: str
    state: LockState
    last_unlock: str | None
    battery: str
    error: str | None
    timestamp: datetime


class VaultPadlockEvents(BaseModel):
    id: str
    event: PadlockEvent
    result: EventResult
    timestamp: datetime


class ControlComputerLock(BaseModel):
    id: str
    lock_state: LockState
    reason: str
    timestamp: datetime

class TokenRequest(BaseModel):
    id: str
    request: str
    timestamp: datetime

class BleToken(BaseModel):
    id: str
    UUID: str
    token: str
    localname: str
    timestamp: datetime

# class StoreToken(BaseModel):
#     id: str
#     token: str
#     UUID: str
#     localname: str
#     timestamp: datetime
