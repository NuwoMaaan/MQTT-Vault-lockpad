from abc import ABC, abstractmethod
import threading
from connection.connect import connect_mqtt
from utils.signal_utils import setup_signal_handlers, shutdown_flag 

class MQTTApp(ABC):
    def __init__(self, id: str):
        setup_signal_handlers()
        self.id = id
        self.client = connect_mqtt(self.id)

    @abstractmethod
    def publish(self):
        pass

    @abstractmethod
    def subscribe(self):
        pass

    def run(self, ble_proc):
        print(f"Device_id: {self.id}")
        threading.Thread(target=self.publish, args=(self.client,)).start()
        threading.Thread(target=self.subscribe, args=(self.client,)).start()

        try:
            while not shutdown_flag.is_set():
                self.client.loop(timeout=1.0)
        except KeyboardInterrupt:
            print("KeyboardInterrupt, shutting down...")
            shutdown_flag.set()
            self.client.loop_stop()
            self.client.disconnect()
            ble_proc.terminate()