from paho.mqtt import client as mqtt_client
from data.control_data_gen import ControlDataGenerator
from utils.console import ascii_art
from schemas.topics import TOPICS
from utils.signal_utils import shutdown_flag
from lock.lockout import publish_lockout, detection_login_attempts
from app.mqtt_app import MQTTApp


class MQTTControlComputerApp(MQTTApp):
    def __init__(self, id: str):
        super().__init__(id)
        self.data = ControlDataGenerator(device_id=self.id)
        
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
            if detection_login_attempts(msg):                                   
                publish_lockout(client, self.data)

        client.subscribe(TOPICS.status)                              
        client.subscribe(TOPICS.metrics)
        client.subscribe(TOPICS.event)  
        client.on_message = on_message


def main():
    app = MQTTControlComputerApp(id="control_device_01")
    ascii_art()
    app.run()
    


if __name__ == '__main__':
    main()

