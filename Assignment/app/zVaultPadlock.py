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
from demo_data.padlock_data_gen import generate_padlock_status_data, generate_padlock_metric_data


def publish(client):                                                        
    try:
        while not shutdown_flag.is_set():
            time.sleep(5)
            if shutdown_flag.is_set():
                break
            padlock_status_data = generate_padlock_status_data()           
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
    threading.Thread(target=subscribe, args=(client,)).start()          
    threading.Thread(target=publish, args=(client,)).start()            
    
    try:
        client.loop_forever()
    except KeyboardInterrupt:
        print("KeyboardInterrupt, shutting down...")
        shutdown_flag.set()
        client.loop_stop()
        client.disconnect()


if __name__ == '__main__':
    run()



