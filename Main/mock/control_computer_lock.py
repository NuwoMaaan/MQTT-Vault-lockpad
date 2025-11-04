
import json
from schemas.topics import TOPICS

def publish_lockout(client):                                    
    issue = (f'MAX ATTEMPTS EXCEED: Overriding lockout control - Access: LOCKED\nSending override to {TOPICS.control}')  
    print(issue)
    client.publish(TOPICS.control, issue)               

def detection_login_attempts(msg):
     if (msg.topic) == TOPICS.metrics:
        print(f"Received `{msg.payload.decode()}`\n\r from `{msg.topic}` topic\n\r")                    
        try:                                                            
            received_message = (msg.payload.decode())    
            if 'Login_attempts' in received_message:
                metrics = json.loads(received_message)        
                attempts = metrics.get('Login_attempts')       
                if int(attempts) > 5:                         
                    return True
            else:
                return False
        except Exception as error:
            return error