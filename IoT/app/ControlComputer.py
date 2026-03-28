from paho.mqtt import client as mqtt_client
from data.control_data_gen import ControlDataGenerator
from schemas.constants import TOPICS
from utils.signal_utils import shutdown_flag
from lock.lockout import publish_lockout, detection_login_attempts
from app.MqttApp import MQTTApp


class MQTTControlComputerApp(MQTTApp):
    def __init__(self, id: str):
        super().__init__(id)
        self.data = ControlDataGenerator(id)
        
    def publish(self, client: mqtt_client): 
        try:
            while not shutdown_flag.is_set():
                # control_data = generator.generate_control_data() # Mock keepalive
                # result_control = client.publish(TOPICS.control, control_data)
                # console_control_out(result_control, control_data)
                pass
        except KeyboardInterrupt:
            print('Program Stopped')

    def subscribe(self, client: mqtt_client):
        def on_message(client, userdata, msg):
            print(f"Received: {msg.payload.decode()}\n\r from {msg.topic}\n\r")
            lock_id = detection_login_attempts(msg)
            if lock_id:                                 
                publish_lockout(client, self.data, lock_id)

        client.subscribe(TOPICS.status)                              
        client.subscribe(TOPICS.metrics)
        client.subscribe(TOPICS.event)  
        client.on_message = on_message


def main():
    app = MQTTControlComputerApp(id="control_device_01")
    app.run(ble_proc=None)
    


if __name__ == '__main__':
    main()

