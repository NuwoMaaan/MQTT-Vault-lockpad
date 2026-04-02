
from schemas.padlock_enums import LockState
from schemas.models import ControlComputerLock
from data.padlock_data_gen import PadlockDataGenerator
import json
from utils.console import console_lock_out

def lock(status_data: PadlockDataGenerator) -> None:
    status_data.state = LockState.indefinite
    status_data.error = "ACCESS FAILURE: TOO MANY UNLOCK ATTEMPTS DETECTED"
    console_lock_out()

def detect_lock_mechanism(msg, host_topic: str) -> bool:                    
    try:
        if (msg.topic) != host_topic:
            return False
                                                               
        data = json.loads(msg.payload.decode())    
        payload = ControlComputerLock.model_validate(data)
        if payload.lock_state == LockState.indefinite:
            return True
        return False
    except Exception as error:
        print(f"Error processing message: {error}")
        return False