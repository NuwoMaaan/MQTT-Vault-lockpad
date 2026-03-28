from paho.mqtt import client as mqtt_client
from schemas.constants import TOPICS
from utils.signal_utils import shutdown_flag
from lock.lock_mechanism import detect_lock_mechanism, lock_mechanism
from services.VaultPadlockService import VaultPadlockService
from data.padlock_data_gen import PadlockDataGenerator
from app.MqttApp import MQTTApp
from app.ble_device import BLEDevice
import time



class MQTTPadlockApp(MQTTApp):
    def __init__(self, id: str):
        super().__init__(id)
        self.passcode = '000'
        self.data = PadlockDataGenerator(id)
        self.ble_device = BLEDevice()
        self.ble_present = False
        self.ble_proc = None
        self.host_topic = f"vault/padlock/{id}"


    def publish(self, client: mqtt_client):
        try:
            while not shutdown_flag.is_set():
                # Generate padlock data
                padlock_status_data = self.data.generate_status_data()
                padlock_metric_data = self.data.generate_metric_data()

                if padlock_status_data is not None:
                    client.publish(TOPICS.status, padlock_status_data)
                if padlock_metric_data is not None:
                    client.publish(TOPICS.metrics, padlock_metric_data)
                time.sleep(5)
        except KeyboardInterrupt:
            print('programmed stopped')

            
    def subscribe(self, client: mqtt_client):
        def on_message(client, userdata, msg):
            print(f"\nReceived `{msg.payload.decode()}`\n\r from `{msg.topic}` topic\n\r")
            if detect_lock_mechanism(msg, self.host_topic):
                lock_mechanism(self.data.status_data)
                
        client.subscribe(TOPICS.control)
        client.subscribe(self.host_topic)
        client.on_message = on_message

            
def main():
    app = MQTTPadlockApp(id="vault_lock_01")
    VaultPadlockService.BLE(app)
    VaultPadlockService.cli_access(app)
    app.run(app.ble_proc)

if __name__ == '__main__':
    main()