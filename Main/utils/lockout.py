import json
from schemas.topics import TOPICS

def publish_lockout(client):                                    
    issue = (f'MAX ATTEMPTS EXCEED: Overriding lockout control - Access: LOCKED\nSending override to {TOPICS.control}')  
    print(issue)
    client.publish(TOPICS.control, issue)               

def detection_login_attempts(msg) -> bool:
    if (msg.topic) == TOPICS.metrics:                    
        try:                                                            
            received_message = (msg.payload.decode())    
            if 'login_attempts' in received_message:
                metrics = json.loads(received_message)        
                attempts = metrics.get('login_attempts') 
                if int(attempts) > 5:                         
                    return True
            else:
                return False
        except Exception as error:
            print(f"Error processing message: {error}")
            return False