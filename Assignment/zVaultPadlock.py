import random
import time
from datetime import datetime
import psutil
import json
import threading
from paho.mqtt import client as mqtt_client

broker = 'rule28.i4t.swin.edu.au'
port = 1883
topics = {
    "control": "<103996982>/padlock/control",
    "status": "<103996982>/padlock/status",
    "metrics": "<103996982>/padlock/metrics",
    "lockout": "<103996982>/padlock/control/lockout"
}
client_id = f'publish-{random.randint(0, 1000)}'
username = '<103996982>'
password = '<103996982>'

def connect_mqtt():
    def on_connect(client, userdata, flags, rc):
        if rc == 0:                                                           #Base code from: https://www.emqx.com/en/blog/how-to-use-mqtt-in-python
            print("Connected to MQTT Broker!")                                #Majority use of mqtt is based from here - then added with my functionality for all programs
        else:
            print("Failed to connect, return code %d\n", rc)

    client = mqtt_client.Client(client_id)
    client.username_pw_set(username, password)
    client.on_connect = on_connect
    client.connect(broker, port)
    return client


def generate_padlock_status_data():                                          #other random data generation for demostration purposes.
    state = random.choice(["locked", "unlocked"])
    error = random.choice([None, "Authorization_failure", "Mechanical_failure", "Malfunction"]) 
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    data = {
        "state": state,
        "error": error,
        "timestamp": timestamp,
    }
    
    return json.dumps(data)                                                 #json.dumps turns python object i.e. dictonary into json string to be sent over network
                                                                            
def generate_padlock_metric_data():
    cpu = psutil.cpu_percent(interval=None)
    cpu_formatted = f"{cpu:.2f}"
    login_attempts = random.randint(1,10)                                   #Change random.randint() to values > 5 for trigger events to not occur.
    network = psutil.net_io_counters()
    netstats = {
        "Packets_recv": str(network.packets_recv),
        "Packets_sent": str(network.packets_sent),
        "Network_Errors": str(network.errin)                                #dictionary within dictionary (data['Network'] = netstats)
        
    }
    
    data = {
        "CPU_Usage": f'{cpu_formatted}%',
        "Login_attempts": login_attempts,                                   #Value that triggers response code from zControlComputer.py
        "Network": netstats
    }
    return json.dumps(data)


def publish(client):                                                        
    try:
        while True:
            time.sleep(5)
            padlock_status_data = generate_padlock_status_data()           #Generating fake data and sending it to appropriate topic.
            padlock_metric_data = generate_padlock_metric_data()
    
            result_status = client.publish(topics['status'], padlock_status_data)
            result_metric = client.publish(topics["metrics"], padlock_metric_data )
            publish_status_status = result_status[0]
            publish_metrics_status = result_metric[0]
            if publish_status_status == 0:
                print(f"Sent: PADLOCK->CONTROL_SYS: {padlock_status_data}, topic: {topics['status']}\n\r")
            else:
                print(f"Failed to send message to topic {topics['status']}")
            if publish_metrics_status == 0:
                print(f"Sent: PADLOCK->CONTROL_SYS: {padlock_metric_data}, topic: {topics['metrics']}\n\r")
            else:
                print(f"Failed to send message to topic {topics['metrics']}")
    except KeyboardInterrupt:
        print('programmed stopped')
        
def subscribe(client: mqtt_client):
    def on_message(client, userdata, msg):
        print(f"Received `{msg.payload.decode()}`\n\r from `{msg.topic}` topic\n\r")

    client.subscribe(topics["control"])
    #client.subscribe(topics["lockout"])
    client.on_message = on_message

def run():
    client = connect_mqtt()
    threading.Thread(target=subscribe, args=(client,)).start()          #Threading to allow for concurrent programming meaning application 
    threading.Thread(target=publish, args=(client,)).start()            #can send and receieve data at the same time. 
    client.loop_forever()


if __name__ == '__main__':
    run()



