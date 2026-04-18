from paho.mqtt import client as mqtt_client
from data.control_data_gen import ControlDataGenerator
from schemas.constants import Topics
from utils.signal_utils import shutdown_flag
from app.MqttApp import MQTTApp
from services.ControlComputerService import ControlComputerService


class MQTTControlComputerApp(MQTTApp):
    def __init__(self, id: str):
        super().__init__(id)
        self.data = ControlDataGenerator(id)
        
    def publish(self, client: mqtt_client): 
        try:
            while not shutdown_flag.is_set():
                # Simulate something like heartbeat ping
                pass
        except KeyboardInterrupt:
            print('Program Stopped')

    def subscribe(self, client: mqtt_client):
        def on_message(client, userdata, msg):
            print(f"Received: {msg.payload.decode()}\n\r from {msg.topic}\n\r")
            ControlComputerService.detection_mechanism(msg, client, self.data.lock_data, self.id)
            ControlComputerService.ble_data_handler(msg, client)

        client.subscribe(Topics.status)                              
        client.subscribe(Topics.metrics)
        client.subscribe(Topics.event)
        client.subscribe(Topics.ble)
        client.on_message = on_message


def main():
    app = MQTTControlComputerApp(id="control_device_01")
    ControlComputerService.start_token_refresh_loop()
    app.run(ble_proc=None)

    


if __name__ == '__main__':
    main()

