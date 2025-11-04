from paho.mqtt import client as mqtt_client
import random
from connections.config import settings

client_id = f'subscribe-{random.randint(0, 100)}'
username = settings.MQTT_USERNAME
password = settings.MQTT_PASSWORD
broker = settings.MQTT_BROKER
port = settings.MQTT_PORT

def on_connect(client, userdata, flags, rc, properties=None):
    if rc == 0:
        print("\nConnected to MQTT Broker!")
    else:
        print(f"Failed to connect, return code {rc}")
                                                                        
def connect_mqtt() -> mqtt_client:                              
    client = mqtt_client.Client(callback_api_version=mqtt_client.CallbackAPIVersion.VERSION2, client_id=client_id)
    client.username_pw_set(username, password)
    client.on_connect = on_connect
    client.connect(broker, port)
    return client

