from paho.mqtt import client as mqtt_client
from schemas.constants import Topics
from utils.signal_utils import shutdown_flag
from services.vault_padlock.VaultPadlockService import VaultPadlockService
from app.MqttApp import MQTTApp
import time


class MQTTPadlockApp(MQTTApp):
    def __init__(self, id: str):
        super().__init__(id)
        self.service = VaultPadlockService(id)
        self.passcode = '000'
        self.host_topic = f"vault/padlock/{id}"


    def publish(self, client: mqtt_client):
        try:
            while not shutdown_flag.is_set():
                # Generate padlock data
                padlock_status_data = self.service.app_data.generate_status_data()
                padlock_metric_data = self.service.app_data.generate_metric_data()

                if padlock_status_data is not None:
                    client.publish(Topics.status, padlock_status_data)
                if padlock_metric_data is not None:
                    client.publish(Topics.metrics, padlock_metric_data)
                time.sleep(20)
        except KeyboardInterrupt:
            print('programmed stopped')

            
    def subscribe(self, client: mqtt_client):
        def on_message(client, userdata, msg):
            print(f"\nReceived `{msg.payload.decode()}`\n\r from `{msg.topic}` topic\n\r")
            self.service.lock_mechanism(msg, self.host_topic, self.service.data.status_data)
                
        client.subscribe(Topics.control)
        client.subscribe(self.host_topic)
        client.on_message = on_message

            
def main():
    app = MQTTPadlockApp(id="vault_lock_01")
    app.service.retrieve_ble_data(app.client, app.host_topic)
    app.service.start_ble()
    app.service.cli_access(app.client, app.passcode)
    app.run(app.service.ble_device.ble_proc)

if __name__ == '__main__':
    main()