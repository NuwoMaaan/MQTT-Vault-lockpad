import json
from schemas.topics import TOPICS
from schemas.controlcomputer import ControlComputerLock
from utils.console import console_lock_out

fail_count = 0

def publish_lockout(client, generator: ControlComputerLock):
    lockout = generator.generate_lock_data()
    if lockout:
        client.publish(TOPICS.control, lockout)
        console_lock_out()

def detection_login_attempts(msg) -> bool:
    global fail_count
    if (msg.topic) == TOPICS.event:                    
        try:                                                            
            received_message = (msg.payload.decode())
            received_message = json.loads(received_message)      
            event = received_message['event']
            result = received_message['result'] 
            if event == 'access_attempt' and result == 'fail':
                if fail_count > 3:
                    fail_count = 0
                    return True
                else:
                    fail_count += 1
            else:
                return False
        except Exception as error:
            print(f"Error processing message: {error}. topic: {msg.topic}")
            return False
        
