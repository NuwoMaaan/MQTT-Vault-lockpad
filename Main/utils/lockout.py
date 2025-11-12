import json
from schemas.topics import TOPICS
from schemas.controlcomputer import ControlComputerLock
from utils.console import console_lock_out
             

def publish_lockout(client, generator: ControlComputerLock):
    lockout = generator.generate_lock_data()
    if lockout:
        client.publish(TOPICS.lockout, lockout)
        console_lock_out()

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
        
