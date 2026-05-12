from schemas.models import ControlComputerLock
from schemas.padlock_enums import LockState
from datetime import datetime, timezone

class ControlDataGenerator:
    def __init__(self, id: str):
        self.device_id = id
        self.lock_data = LockData(id)
    
class LockData():
    def __init__(self, id: str):
        self.id = id

    def generate_lock_data(self) -> ControlComputerLock: 
        try:
            timestamp = datetime.now(timezone.utc)
            data = ControlComputerLock(
                id=self.id,
                lock_state=LockState.indefinite,
                reason="Consecutive failed access attempts",
                timestamp=timestamp
            )
        except Exception as e:
            print("Error:", e)
            return None
        
        return data

    
    

      