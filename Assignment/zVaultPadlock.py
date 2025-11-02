import random
import time
from datetime import datetime
import psutil
import json
import threading
from paho.mqtt import client as mqtt_client
from connections.connect import connect_mqtt
from schemas.topics import TOPICS
from Assignment.utils.signal_utils import setup_signal_handlers, shutdown_flag


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
        while not shutdown_flag.is_set():
            time.sleep(5)
            if shutdown_flag.is_set():
                break
            padlock_status_data = generate_padlock_status_data()           #Generating fake data and sending it to appropriate topic.
            padlock_metric_data = generate_padlock_metric_data()

            result_status = client.publish(TOPICS.status, padlock_status_data)
            result_metric = client.publish(TOPICS.metrics, padlock_metric_data)
            publish_status_status = result_status[0]
            publish_metrics_status = result_metric[0]
            if publish_status_status == 0:
                print(f"Sent: PADLOCK->CONTROL_SYS: {padlock_status_data}, topic: {TOPICS.status}\n\r")
            else:
                print(f"Failed to send message to topic {TOPICS.status}")
            if publish_metrics_status == 0:
                print(f"Sent: PADLOCK->CONTROL_SYS: {padlock_metric_data}, topic: {TOPICS.metrics}\n\r")
            else:
                print(f"Failed to send message to topic {TOPICS.metrics}")
    except KeyboardInterrupt:
        print('programmed stopped')
        
def subscribe(client: mqtt_client):
    def on_message(client, userdata, msg):
        print(f"Received `{msg.payload.decode()}`\n\r from `{msg.topic}` topic\n\r")

    client.subscribe(TOPICS.control)
    #client.subscribe(topics["lockout"])
    client.on_message = on_message

def run():
    setup_signal_handlers()
    client = connect_mqtt()
    threading.Thread(target=subscribe, args=(client,)).start()          #Threading to allow for concurrent programming meaning application 
    threading.Thread(target=publish, args=(client,)).start()            #can send and receieve data at the same time. 
    
    try:
        client.loop_forever()
    except KeyboardInterrupt:
        print("KeyboardInterrupt, shutting down...")
        shutdown_flag.set()
        client.loop_stop()
        client.disconnect()


if __name__ == '__main__':
    run()



