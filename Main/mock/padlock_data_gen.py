import random
import json
import psutil
import time
from datetime import datetime
from schemas.vaultpadlock import VaultPadlockMetrics, VaultPadlockStatus
from pydantic import ValidationError


class PadlockDataGenerator:
    def __init__(self):
        self.login_attempts = 1

    def generate_padlock_status_data(self) -> VaultPadlockStatus:
        time.sleep(5)                                         
        state = random.choice(["locked", "unlocked"])
        error = random.choice([None, "Authorization_failure", "Mechanical_failure", "Malfunction"]) 
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            data = VaultPadlockStatus(
                id="padlock_1",
                state=state,
                error=error,
                timestamp=timestamp,
                )
        except ValidationError as e:
            print("Validation error:", e)
            return None

        return data.model_dump_json()


    def generate_padlock_metric_data(self) -> VaultPadlockMetrics:
        time.sleep(5)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cpu = psutil.cpu_percent(interval=None)
        cpu_formatted = f"{cpu:.2f}"                                
        network = psutil.net_io_counters()
        netstats = {
            "Packets_recv": str(network.packets_recv),
            "Packets_sent": str(network.packets_sent),
            "Network_Errors": str(network.errin)                                  
        }

        if self.login_attempts == 6:
            self.login_attempts = 1
        else:
            self.login_attempts += 1

        try:
            data = VaultPadlockMetrics(
                id="padlock_1",
                cpu=cpu_formatted,
                login_attempts=self.login_attempts,
                netstats=netstats,
                timestamp=timestamp,
                )
        except ValidationError as e:
            print("Validation error:", e)
            return None
        
        return data.model_dump_json()