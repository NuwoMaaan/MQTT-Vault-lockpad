import random
import psutil
import time
from datetime import datetime, timezone
from schemas.models import VaultPadlockMetrics, VaultPadlockStatus, VaultPadlockEvents
from schemas.constants import TOPICS
from pydantic import ValidationError


class PadlockDataGenerator():
    def __init__(self, id: str):
        self.device_id = id
        self.status_data = StatusData(id)
        self.metric_data = MetricData(id)
        self.event_data = EventData(id)

    def generate_status_data(self) -> str | None:
        return _generate_padlock_status_data(self.status_data).model_dump_json()

    def generate_metric_data(self) -> str | None:
        return _generate_padlock_metric_data(self.metric_data).model_dump_json()

    def generate_event_data(self, event: str, result: str) -> str | None:
        self.event_data.event = event
        self.event_data.result = result
        return _generate_padlock_event_data(self.event_data).model_dump_json()

class StatusData():
    def __init__(self, id: str):
        self.device_id = id
        self.state = "LOCKED"
        self.last_unlock = None
        self.battery = "94%"
        self.error = None

def _generate_padlock_status_data(data: StatusData) -> VaultPadlockStatus | None:                                         
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S")
    try:
        status_data = VaultPadlockStatus(
            id=data.device_id,
            state=data.state,
            last_unlock=data.last_unlock,
            battery=data.battery,
            error=data.error,
            timestamp=timestamp,
            )
    except ValidationError as e:
        print("Validation error:", e)
        return None
    
    return status_data

    
class MetricData():
    def __init__(self, id: str):
        self.device_id = id
        self.unlock_attempts = 1
        self.cpu_formatted = None
        self.temperature = None
        
def _generate_padlock_metric_data(data: MetricData) -> VaultPadlockMetrics | None:
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S")
    cpu = psutil.cpu_percent(interval=None)
    data.cpu_formatted = f"{cpu:.2f}%"
    data.temperature = f"{random.randint(30, 40)} C"
    try:
        metric_data = VaultPadlockMetrics(
            id=data.device_id,
            cpu=data.cpu_formatted,
            temperature=data.temperature,
            timestamp=timestamp,
            )
    except ValidationError as e:
        print("Validation error:", e)
        return None
    
    return metric_data


class EventData():
    def __init__(self, id: str):
        self.device_id = id 
        self.event = None
        self.result = None
    
def _generate_padlock_event_data(data: EventData) -> VaultPadlockEvents | None:
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S")
    try:
        event_data = VaultPadlockEvents(
            id=data.device_id,
            event=data.event,
            result=data.result,
            timestamp=timestamp
        )
    except ValidationError as e:
        print("Validation Error:", e)
        return None
    
    return event_data
    