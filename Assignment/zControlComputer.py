import random
import time
import threading
import json
from paho.mqtt import client as mqtt_client

broker = 'broker.emqx.io'
#broker = 'rule28.i4t.swin.edu.au'
port = 1883
topics = {
    "control": "<103996982>/padlock/control",
    "status": "<103996982>/padlock/status",
    "metrics": "<103996982>/padlock/metrics",
    "lockout": "<103996982>/padlock/control/lockout"
}


client_id = f'subscribe-{random.randint(0, 100)}'
username = '<103996982>'
password = '<103996982>'


def connect_mqtt() -> mqtt_client:
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:                                                                 #Base code from: https://www.emqx.com/en/blog/how-to-use-mqtt-in-python
            print("Failed to connect, return code %d\n", rc)                  #Majority use of mqtt is based from here - then added with my functionality

    client = mqtt_client.Client(client_id)
    client.username_pw_set(username, password)
    client.on_connect = on_connect
    client.connect(broker, port)
    return client

def publish(client):
    try:
        while True:
            time.sleep(5)
            control = random.choice(['OPEN','CLOSE'])                    #constant sending of arbitruary fake data for demostration purposes
            result = client.publish(topics["control"], control)
            # result: [0, 1]
            status = result[0]                                           
            if status == 0:
                print(f"Sent: CONTROL_SYS->PADLOCK: {control}, topic: {topics['control']}\n\r")
            else:
                print(f"Failed to send message to topic {topics['control']}")
    except KeyboardInterrupt:
        print('Program Stopped')

def publish_lockout(client):                                     #send to control topic to override padlock
    issue = (f'MAX ATTEMPTS EXCEED: Overriding lockout control - Access: LOCKED\nSending override to {topics["control"]}')  
    print(issue)
    client.publish(topics["control"], issue)               

def detection_login_attempts(msg):
     if (msg.topic) == topics["metrics"]:                       #validate this is message from dependent topic
        try:                                                            
            received_message = (msg.payload.decode())    
            if 'Login_attempts' in received_message:
                metrics = json.loads(received_message)          #Generated data is formatted with json.dumps(), json.loads() turns back into python object able to be worked with
                attempts = metrics.get('Login_attempts')        #get Login_attempts key value
                if int(attempts) > 5:                           #convert to int, verify variable has exceeded limit
                    return True
            else:
                return False
        except:
            return False

def subscribe(client: mqtt_client):
    def on_message(client, userdata, msg):
        print(f"Received `{msg.payload.decode()}`\n\r from `{msg.topic}` topic\n\r")
        if detection_login_attempts(msg):                                               #Checking if value is over certain value to determine if command should be sent to client
            publish_lockout(client)                                                     #If true, publish_lockout method sends to defined topic
        else:
            pass

    client.subscribe(topics['status'])
    #client.subscribe(topic['control'])                                     
    client.subscribe(topics["metrics"])
    client.on_message = on_message


def run():
    client = connect_mqtt()
    threading.Thread(target=subscribe, args=(client,)).start()          #Threading to allow for concurrent programming meaning application 
    threading.Thread(target=publish, args=(client,)).start()            #can send and receieve data at the same time. 
    client.loop_forever()
    


if __name__ == '__main__':
    run()

