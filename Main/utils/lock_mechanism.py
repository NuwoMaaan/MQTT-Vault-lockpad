
from schemas.topics import TOPICS
from mock.padlock_data_gen import PadlockDataGenerator
from utils.console import console_lock_out
import json


def lock_mechanism(generator: PadlockDataGenerator) -> None:
    generator.state = "INDEFINITE_LOCKED"

def detect_lock_mechanism(msg) -> bool:
    if (msg.topic) == TOPICS.control:                    
        try:                                                            
            received_message = (msg.payload.decode())    
            control = json.loads(received_message)
            lockout_state = control.get('lock_state') 
            if lockout_state == "INDEFINITE_LOCK":
                return True
            return False
        except Exception as error:
            print(f"Error processing message: {error}")
            return False