
from schemas.controlcomputer import ControlComputerLock
from pydantic import ValidationError

class ControlDataGenerator:
    def __init__(self):
        pass
    
    def generate_lock_data(self, device_id): 
        try:
            data = ControlComputerLock(
                id=device_id,
                lock_state="INDEFINITE_LOCK",
                reason="brute force attempt"
            )
        except ValidationError as e:
            print("Validation error:", e)
            return None
        
        return data.model_dump_json()
    
    

      