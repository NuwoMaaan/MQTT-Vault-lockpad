import time
import threading
from paho.mqtt import client as mqtt_client
from connections.connect import connect_mqtt
from schemas.topics import TOPICS
from utils.signal_utils import setup_signal_handlers, shutdown_flag
from mock.padlock_data_gen import generate_padlock_status_data, generate_padlock_metric_data
from utils.console import console_out


def publish(client):                                                        
    try:
        while not shutdown_flag.is_set():
            padlock_status_data, padlock_metric_data = generate_padlock_status_data(), generate_padlock_metric_data()

            result_status = client.publish(TOPICS.status, padlock_status_data)
            result_metric = client.publish(TOPICS.metrics, padlock_metric_data)
            
            console_out(result_status, result_metric, padlock_status_data, padlock_metric_data)
    except KeyboardInterrupt:
        print('programmed stopped')
        
def subscribe(client: mqtt_client):
    def on_message(client, userdata, msg):
        print(f"Received `{msg.payload.decode()}`\n\r from `{msg.topic}` topic\n\r")

    client.subscribe(TOPICS.control)
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



