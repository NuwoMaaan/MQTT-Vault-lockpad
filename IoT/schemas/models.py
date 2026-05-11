from datetime import datetime
import json
from dataclasses import asdict, dataclass
from typing import TypeVar, Type
from schemas.padlock_enums import LockState, PadlockEvent, EventResult


T = TypeVar("T", bound="SerializableMixin")

class SerializableMixin:
    def to_json(self):
        return json.dumps(asdict(self), default=str)
    
    @classmethod
    def from_dict(cls: Type[T], data: dict) -> T:
        return cls(**data)
    
#model_validate() = from_dict
#mode_dump_json() = to_json
    
@dataclass(slots=True)
class VaultPadlockMetrics(SerializableMixin):
    id: str
    cpu: str
    temperature: str
    timestamp: datetime


@dataclass(slots=True)
class VaultPadlockStatus(SerializableMixin):
    id: str
    state: LockState
    last_unlock: str | None
    battery: str
    error: str | None
    timestamp: datetime

@dataclass(slots=True)
class VaultPadlockEvents(SerializableMixin):
    id: str
    event: PadlockEvent
    result: EventResult
    timestamp: datetime

@dataclass(slots=True)
class ControlComputerLock(SerializableMixin):
    id: str
    lock_state: LockState
    reason: str
    timestamp: datetime

@dataclass(slots=True)
class BleDataRequest(SerializableMixin):
    id: str
    request: str
    timestamp: datetime

@dataclass(slots=True)
class BleData(SerializableMixin):
    id: str
    UUID: str
    token: str
    localname: str
    timestamp: datetime

