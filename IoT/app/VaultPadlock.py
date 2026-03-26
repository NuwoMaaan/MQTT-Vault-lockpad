from paho.mqtt import client as mqtt_client
from schemas.constants import TOPICS
from utils.signal_utils import shutdown_flag
from data.padlock_data_gen import PadlockDataGenerator
from utils.console import console_padlock_out, ascii_art
from app.MqttApp import MQTTApp
from app.ble_device import BLEDevice
from lock.lock_mechanism import detect_lock_mechanism, lock_mechanism
import threading

from pathlib import Path
import subprocess
import json



class MQTTPadlockApp(MQTTApp):
    def __init__(self, id: str):
        super().__init__(id)
        self.data = PadlockDataGenerator()
        self.ble_device = BLEDevice()
        self.ble_present = False
        self.ble_proc = None
        self.host_topic = f"vault/padlock/{self.id}"


    def publish(self, client: mqtt_client):
        try:
            while not shutdown_flag.is_set():
                # Generate padlock data
                padlock_status_data = self.data.generate_padlock_status_data(self.id)
                padlock_metric_data = self.data.generate_padlock_metric_data(self.id)
                padlock_event_data = self.data.generate_padlock_event_data(self.id)

                result_status = client.publish(TOPICS.status, padlock_status_data)
                result_metric = client.publish(TOPICS.metrics, padlock_metric_data)
                result_event = client.publish(TOPICS.event, padlock_event_data)

                console_padlock_out(result_status, padlock_status_data,
                                    result_metric,  padlock_metric_data,
                                    result_event, padlock_event_data
                )
        except KeyboardInterrupt:
            print('programmed stopped')
            
    def subscribe(self, client: mqtt_client):
        def on_message(client, userdata, msg):
            print(f"Received `{msg.payload.decode()}`\n\r from `{msg.topic}` topic\n\r")
            if detect_lock_mechanism(msg, self.host_topic):
                lock_mechanism(self.data)
                
        client.subscribe(TOPICS.control)
        client.subscribe(self.host_topic)
        client.on_message = on_message
            
    
    def detect_BLE_device(self):
        ble_cmd_dir = Path(__file__).resolve().parents[2] / "BLE" / "cmd"

        self.ble_present = False
        self.ble_proc = subprocess.Popen(
            ["go", "run", "./main.go", "detect"],
            cwd=ble_cmd_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
        )
        def reader():
            for line in self.ble_proc.stdout:
                line = line.strip()
                if not line:
                    continue
            
                try:
                    event = json.loads(line)
                    if "Present" in event:
                        self.ble_present = bool(event["Present"])
                        print(event)
                    if "LocalName" in event:
                        self.ble_device.local_name = event.get('LocalName')
                        self.ble_device.token = event.get('Token')
                        self.ble_device.UUID = event.get('DeviceUUID')
                        print(self.ble_device)
                except json.JSONDecodeError:
                    continue

        threading.Thread(target=reader, daemon=True).start()
            


def main():
    app = MQTTPadlockApp(id="vault_lock_01")
    ascii_art()
    app.detect_BLE_device()
    app.run(app.ble_proc)

if __name__ == '__main__':
    main()