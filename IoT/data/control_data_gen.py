
from schemas.models import ControlComputerLock
from pydantic import ValidationError
from schemas.padlock_enums import LockState
from datetime import datetime, timezone

class ControlDataGenerator:
    def __init__(self, id: str):
        self.device_id = id
    
    def generate_lock_data(self) -> ControlComputerLock: 
        try:
            timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S")
            data = ControlComputerLock(
                id=self.device_id,
                lock_state=LockState.indefinite,
                reason="Consecutive failed access attempts",
                timestamp=timestamp
            )
        except ValidationError as e:
            print("Validation error:", e)
            return None
        
        return data
    
    

      