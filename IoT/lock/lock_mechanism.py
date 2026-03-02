
from schemas.constants import TOPICS
from schemas.padlock_enums import LockState
from schemas.models import ControlComputerLock
from data.padlock_data_gen import PadlockDataGenerator
import json, time
from utils.console import console_lock_out

def lock_mechanism(generator: PadlockDataGenerator) -> None:
    generator.state = LockState.indefinite
    generator.error = "ACCESS FAILURE: TOO MANY UNLOCK ATTEMPTS DETECTED"
    console_lock_out()
    # Reset to lock state to continue mock functionality
    # But also sleep to show lock state and error change
    # After 30 seconds, attributes return to default
    time.sleep(30)
    generator.state = LockState.locked
    generator.error = None

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