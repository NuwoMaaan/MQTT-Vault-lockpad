import random
import psutil
import time
from datetime import datetime
from schemas.models import VaultPadlockMetrics, VaultPadlockStatus, VaultPadlockEvents
from pydantic import ValidationError


class PadlockDataGenerator:
    def __init__(self):
        # common attributes
        self.device_id = ""
        self.timestamp = None
        # specific to metrics
        self.unlock_attempts = 1
        self.cpu_formatted = None
        self.temperature = None
        # specific to status
        self.state = "LOCKED"
        self.last_unlock = None
        self.battery = "94%"
        self.error = None

    

    def generate_padlock_status_data(self, device_id) -> VaultPadlockStatus:
        time.sleep(5)                                         
         
        self.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            data = VaultPadlockStatus(
                id=device_id,
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


    def generate_padlock_metric_data(self, device_id) -> VaultPadlockMetrics:
        time.sleep(5)
        self.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cpu = psutil.cpu_percent(interval=None)
        self.cpu_formatted = f"{cpu:.2f}%"
        self.temperature = f"{random.randint(30, 40)} C"

        try:
            data = VaultPadlockMetrics(
                id=device_id,
                cpu=self.cpu_formatted,
                temperature=self.temperature,
                timestamp=self.timestamp,
                )
        except ValidationError as e:
            print("Validation error:", e)
            return None
        
        return data.model_dump_json()

    def generate_padlock_event_data(self, device_id) -> VaultPadlockEvents:
        time.sleep(5)
        self.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if self.unlock_attempts == 3: 
            self.unlock_attempts = 1
        else:
            self.unlock_attempts += 1

        try:
            data = VaultPadlockEvents(
                id=device_id,
                event="access_attempt",
                result="fail",
                timestamp=self.timestamp
            )
        except ValidationError as e:
            print("Validation Error:", e)
            return None
        
        return data.model_dump_json()