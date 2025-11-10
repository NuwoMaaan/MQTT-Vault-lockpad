import random
import psutil
import time
from datetime import datetime
from schemas.vaultpadlock import VaultPadlockMetrics, VaultPadlockStatus
from pydantic import ValidationError


class PadlockDataGenerator:
    def __init__(self):
        # common attributes
        self.id = "padlock_1"
        self.timestamp = None
        # specific to metrics
        self.unlock_attempts = 1
        self.netstats = {}
        self.cpu_formatted = None
        self.temperature = None
        # specific to status
        self.state = "LOCKED"
        self.last_unlock = None
        self.battery = "94%"
        self.error = None

    

    def generate_padlock_status_data(self) -> VaultPadlockStatus:
        time.sleep(5)                                         
         
        self.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            data = VaultPadlockStatus(
                id=self.id,
                state=self.state,
                last_unlock=self.last_unlock,
                battery=self.battery,
                error=self.error,
                timestamp=self.timestamp,
                )
        except ValidationError as e:
            print("Validation error:", e)
            return None

        return data.model_dump_json()


    def generate_padlock_metric_data(self) -> VaultPadlockMetrics:
        time.sleep(5)
        self.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cpu = psutil.cpu_percent(interval=None)
        self.cpu_formatted = f"{cpu:.2f}%"
        self.temperature = f"{random.randint(30, 40)} C"
        network = psutil.net_io_counters()
        self.netstats = {
            "Packets_recv": str(network.packets_recv),
            "Packets_sent": str(network.packets_sent),
            "Network_Errors": str(network.errin)                                  
        }

        if self.unlock_attempts == 6:
            self.unlock_attempts = 1
        else:
            self.unlock_attempts += 1

        try:
            data = VaultPadlockMetrics(
                id=self.id,
                cpu=self.cpu_formatted,
                temperature=self.temperature,
                unlock_attempts=self.unlock_attempts,
                netstats=self.netstats,
                timestamp=self.timestamp,
                )
        except ValidationError as e:
            print("Validation error:", e)
            return None
        
        return data.model_dump_json()
        