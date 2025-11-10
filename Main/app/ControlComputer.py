from paho.mqtt import client as mqtt_client
from mock.control_data_gen import ControlDataGenerator
from utils.console import console_control_out
from schemas.topics import TOPICS
from utils.signal_utils import shutdown_flag
from utils.lockout import publish_lockout, detection_login_attempts
from utils.mqtt_app import MQTTApp


control_data_generator = ControlDataGenerator()

class MQTTControlComputerApp(MQTTApp):
    def publish(self, client: mqtt_client): 
        try:
            while not shutdown_flag.is_set():
                control_data = control_data_generator.generate_control_data() # Mock keepalive
                result_control = client.publish(TOPICS.control, control_data)
                console_control_out(result_control, control_data)
        except KeyboardInterrupt:
            print('Program Stopped')

    def subscribe(self, client: mqtt_client):
        def on_message(client, userdata, msg):
            print(f"Received: {msg.payload.decode()}\n\r from {msg.topic}\n\r")
            if detection_login_attempts(msg):                                      
                publish_lockout(client)

            

        client.subscribe(TOPICS.status)                              
        client.subscribe(TOPICS.metrics)    
        client.on_message = on_message


def main():
    app = MQTTControlComputerApp()
    app.run()
    


if __name__ == '__main__':
    main()

