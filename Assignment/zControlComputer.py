import random
import time
import threading
import json
import signal
import sys
from paho.mqtt import client as mqtt_client
from connections.connect import connect_mqtt
from schemas.topics import Topics

# Create an instance of Topics to access the topic strings
topics = Topics()

# Global flag for graceful shutdown
shutdown_flag = threading.Event()

def signal_handler(sig, frame):
    print('\nShutdown signal received. Stopping...')
    shutdown_flag.set()
    sys.exit(0)

def publish(client):
    try:
        while not shutdown_flag.is_set():
            time.sleep(5)
            if shutdown_flag.is_set():
                break
            control = random.choice(['OPEN','CLOSE'])                    #constant sending of arbitruary fake data for demostration purposes
            result = client.publish(topics.control, control)
            # result: [0, 1]
            status = result[0]                                           
            if status == 0:
                print(f"Sent: CONTROL_SYS->PADLOCK: {control}, topic: {topics.control}\n\r")
            else:
                print(f"Failed to send message to topic {topics.control}")
    except KeyboardInterrupt:
        print('Program Stopped')

def publish_lockout(client):                                     #send to control topic to override padlock
    issue = (f'MAX ATTEMPTS EXCEED: Overriding lockout control - Access: LOCKED\nSending override to {topics.control}')  
    print(issue)
    client.publish(topics.control, issue)               

def detection_login_attempts(msg):
     if (msg.topic) == topics.metrics:
        print(f"Received `{msg.payload.decode()}`\n\r from `{msg.topic}` topic\n\r")                    
        try:                                                            
            received_message = (msg.payload.decode())    
            if 'Login_attempts' in received_message:
                metrics = json.loads(received_message)          #Generated data is formatted with json.dumps(), json.loads() turns back into python object able to be worked with
                attempts = metrics.get('Login_attempts')        #get Login_attempts key value
                if int(attempts) > 5:                           #convert to int, verify variable has exceeded limit
                    return True
            else:
                return False
        except Exception as error:
            return error

def subscribe(client: mqtt_client):
    def on_message(client, userdata, msg):
        if detection_login_attempts(msg):                                      
            publish_lockout(client)

    client.subscribe(topics.status)                                
    client.subscribe(topics.metrics)
    client.on_message = on_message


def run():
    # Set up signal handler for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    
    client = connect_mqtt()
    threading.Thread(target=subscribe, args=(client,)).start()          #Threading to allow for concurrent programming meaning application 
    threading.Thread(target=publish, args=(client,)).start()            #can send and receieve data at the same time. 
    
    try:
        client.loop_forever()
    except KeyboardInterrupt:
        print("Received KeyboardInterrupt, shutting down...")
        shutdown_flag.set()
        client.loop_stop()
        client.disconnect()
    


if __name__ == '__main__':
    run()

