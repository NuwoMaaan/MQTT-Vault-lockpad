
from schemas.topics import TOPICS
from mock.padlock_data_gen import PadlockDataGenerator
import json, time


def lock_mechanism(generator: PadlockDataGenerator) -> None:
    generator.state = "INDEFINITE_LOCKED"
    generator.error = "ACCESS FAILURE: TOO MANY UNLOCK ATTEMPTS DETECTED"
    # Reset to lock state to continue mock functionality
    # But also sleep to show lock state and error change
    # After 30 seconds, attributes return to default
    time.sleep(30)
    generator.state = "LOCKED"
    generator.error = None

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