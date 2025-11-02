import random
import time
from paho.mqtt import client as mqtt_client
from schemas.topics import TOPICS
from utils.signal_utils import shutdown_flag
from utils.lockout import publish_lockout, detection_login_attempts
from utils.MqttApp import MQTTApp


class MQTTControlComputerApp(MQTTApp):
    def publish(self, client: mqtt_client): 
        try:
            while not shutdown_flag.is_set():
                time.sleep(5)
                if shutdown_flag.is_set():
                    break
                control = random.choice(['OPEN','CLOSE'])                    
                result = client.publish(TOPICS.control, control)
                # result: [0, 1]
                status = result[0]                                           
                if status == 0:
                    print(f"{result[1]} Sent: CONTROL_SYS->PADLOCK: {control}, topic: {TOPICS.control}\n\r")
                else:
                    print(f"Failed to send message to topic {TOPICS.control}")
        except KeyboardInterrupt:
            print('Program Stopped')

    def subscribe(self, client: mqtt_client):
        def on_message(client, userdata, msg):
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

