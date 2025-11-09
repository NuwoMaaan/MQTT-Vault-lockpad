
from schemas.topics import TOPICS
from schemas.controlcomputer import ControlComputerKeepAlive
from pydantic import ValidationError
import time

class ControlDataGenerator:
    def __init__(self):
        pass

    def generate_control_data(self):
        time.sleep(25)
        message = 'KEEPALIVE'
    
        try:
            data = ControlComputerKeepAlive(
                id="control_1",
                keepalive=message
            )
        except ValidationError as e:
            print("Validation error:", e)
            return None
        
        return data.model_dump_json()

      