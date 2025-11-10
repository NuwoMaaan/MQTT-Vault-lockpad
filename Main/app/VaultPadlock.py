from paho.mqtt import client as mqtt_client
from schemas.topics import TOPICS
from utils.signal_utils import shutdown_flag
from mock.padlock_data_gen import PadlockDataGenerator
from utils.console import console_padlock_out, console_lock_out
from utils.mqtt_app import MQTTApp
from utils.lock_mechanism import detect_lock_mechanism, lock_mechanism

generator = PadlockDataGenerator()

class MQTTPadlockApp(MQTTApp):
    def publish(self, client: mqtt_client):
        try:
            while not shutdown_flag.is_set():
                # Generate padlock data
                padlock_status_data = generator.generate_padlock_status_data()
                padlock_metric_data = generator.generate_padlock_metric_data()

                result_status = client.publish(TOPICS.status, padlock_status_data)
                result_metric = client.publish(TOPICS.metrics, padlock_metric_data)

                console_padlock_out(result_status, result_metric, padlock_status_data, padlock_metric_data)
        except KeyboardInterrupt:
            print('programmed stopped')
            
    def subscribe(self, client: mqtt_client):
        def on_message(client, userdata, msg):
            print(f"Received `{msg.payload.decode()}`\n\r from `{msg.topic}` topic\n\r")
            if detect_lock_mechanism(msg):
                lock_mechanism(generator)
                console_lock_out(msg)
                
        client.subscribe(TOPICS.control)
        client.on_message = on_message

def main():
    app = MQTTPadlockApp()
    app.run()

if __name__ == '__main__':
    main()