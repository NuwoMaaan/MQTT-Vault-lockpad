from paho.mqtt import client as mqtt_client
from data.control_data_gen import ControlDataGenerator
from schemas.constants import Topics
from utils.signal_utils import shutdown_flag
from app.MqttApp import MQTTApp
from services.control_computer.ControlComputerService import ControlComputerService


class MQTTControlComputerApp(MQTTApp):
    def __init__(self, id: str):
        super().__init__(id)
        self.data = ControlDataGenerator(id)
        self.service = ControlComputerService()
        
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
            self.service.detection_mechanism(msg, client, self.data.lock_data, self.id)
            self.service.ble_data_handler(msg, client)

        client.subscribe(Topics.status)                              
        client.subscribe(Topics.metrics)
        client.subscribe(Topics.event)
        client.subscribe(Topics.ble)
        client.on_message = on_message


def main():
    app = MQTTControlComputerApp(id="control_device_01")
    app.service.start_jwt_refresh_loop()
    app.run()

    


if __name__ == '__main__':
    main()

