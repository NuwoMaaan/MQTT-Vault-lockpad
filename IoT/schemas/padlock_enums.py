from enum import StrEnum

class LockState(StrEnum):
    locked = "LOCKED"
    unlocked = "UNLOCKED"
    indefinite = "INDEFINITE_LOCK"


class PadlockEvent(StrEnum):
    access_attempt = "access_attempt"
    heartbeat = "heartbeat"


class EventResult(StrEnum):
    success = "success"
    fail = "fail"
    denied = "denied"

class BleDevice(StrEnum):
    localname = "LocalName"
    token = "Token"
    deviceUUID = "DeviceUUID"
    present = "Present"
