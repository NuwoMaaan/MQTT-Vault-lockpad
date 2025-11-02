from paho.mqtt import client as mqtt_client
from schemas.topics import TOPICS
from utils.signal_utils import shutdown_flag
from mock.padlock_data_gen import generate_padlock_status_data, generate_padlock_metric_data
from utils.console import console_out
from utils.MqttApp import MQTTApp


class MQTTPadlockApp(MQTTApp):
    def publish(self, client: mqtt_client):
        try:
            while not shutdown_flag.is_set():
                padlock_status_data, padlock_metric_data = generate_padlock_status_data(), generate_padlock_metric_data()

                result_status = client.publish(TOPICS.status, padlock_status_data)
                result_metric = client.publish(TOPICS.metrics, padlock_metric_data)
                
                console_out(result_status, result_metric, padlock_status_data, padlock_metric_data)
        except KeyboardInterrupt:
            print('programmed stopped')
            
    def subscribe(self, client: mqtt_client):
        def on_message(client, userdata, msg):
            print(f"Received `{msg.payload.decode()}`\n\r from `{msg.topic}` topic\n\r")

        client.subscribe(TOPICS.control)
        client.on_message = on_message

def main():
    app = MQTTPadlockApp()
    app.run()

if __name__ == '__main__':
    main()