import json
from schemas.topics import TOPICS
from schemas.controlcomputer import ControlComputerLock
from pydantic import ValidationError
             

def publish_lockout(client):
    try:
        data = ControlComputerLock(
            id="control_1",
            lock_state="INDEFINITE_LOCK"
        )
    except ValidationError as e:
        print("Validation error:", e)
        return None

    client.publish(TOPICS.control, data.model_dump_json())

def detection_login_attempts(msg) -> bool:
    if (msg.topic) == TOPICS.metrics:                    
        try:                                                            
            received_message = (msg.payload.decode())    
            if 'unlock_attempts' in received_message:
                metrics = json.loads(received_message)        
                attempts = metrics.get('unlock_attempts') 
                if int(attempts) > 5:                         
                    return True
            else:
                return False
        except Exception as error:
            print(f"Error processing message: {error}")
            return False
        
