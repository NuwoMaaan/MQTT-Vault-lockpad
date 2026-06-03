import random
import psutil
from datetime import datetime, timezone
from schemas.models import VaultPadlockMetrics, VaultPadlockStatus, VaultPadlockEvents


class PadlockDataGenerator():
    def __init__(self, id: str):
        self.status_data = StatusData(id)
        self.metric_data = MetricData(id)
        self.event_data = EventData(id)

    def generate_status_data(self) -> str | None:
        return self.status_data.generate_padlock_status_data().to_json()

    def generate_metric_data(self) -> str | None:
        return self.metric_data.generate_padlock_metric_data().to_json()

    def generate_event_data(self, event: str, result: str) -> str | None:
        return self.event_data.generate_padlock_event_data(event, result).to_json()
    

class StatusData():
    def __init__(self, id: str):
        self.device_id = id
        self.state = "LOCKED"
        self.last_unlock = None
        self.battery = None
        self.error = None

    def generate_padlock_status_data(self) -> VaultPadlockStatus | None:                                         
        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S")
        battery = f"{psutil.sensors_battery().percent:.2f}%"
        try:
            status_data = VaultPadlockStatus(
                id=self.device_id,
                state=self.state,
                last_unlock=self.last_unlock,
                battery=battery,
                error=self.error,
                timestamp=timestamp,
                )
        except Exception as e:
            print("Error:", e)
            return None
        
        return status_data

    
class MetricData():
    def __init__(self, id: str):
        self.device_id = id
        self.unlock_attempts = 1
        self.cpu_formatted = None
        self.temperature = None
        
    def generate_padlock_metric_data(self) -> VaultPadlockMetrics | None:
        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S")
        cpu = psutil.cpu_percent(interval=None)
        self.cpu_formatted = f"{cpu:.2f}%"
        self.temperature = f"{random.randint(30, 40)} C"
        try:
            metric_data = VaultPadlockMetrics(
                id=self.device_id,
                cpu=self.cpu_formatted,
                temperature=self.temperature,
                timestamp=timestamp,
                )
        except Exception as e:
            print("Error:", e)
            return None
        
        return metric_data


class EventData():
    def __init__(self, id: str):
        self.device_id = id 
        self.event = None
        self.result = None
    
    def generate_padlock_event_data(self, event: str, result: str) -> VaultPadlockEvents | None:
        self.event = event
        self.result = result
        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S")
        try:
            event_data = VaultPadlockEvents(
                id=self.device_id,
                event=self.event,
                result=self.result,
                timestamp=timestamp
            )
        except Exception as e:
            print("Error:", e)
            return None
        
        return event_data
        