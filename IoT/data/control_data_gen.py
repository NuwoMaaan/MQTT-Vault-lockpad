
from schemas.models import ControlComputerLock
from pydantic import ValidationError

from datetime import datetime

class ControlDataGenerator:
    def __init__(self):
        pass
    
    def generate_lock_data(self, device_id): 
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            data = ControlComputerLock(
                id=device_id,
                lock_state="INDEFINITE_LOCK",
                reason="brute force attempt",
                timestamp=timestamp
            )
        except ValidationError as e:
            print("Validation error:", e)
            return None
        
        return data.model_dump_json()
    
    

      