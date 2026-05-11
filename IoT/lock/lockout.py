import json
from data.control_data_gen import LockData
from schemas.constants import Topics
from schemas.models import VaultPadlockEvents
from schemas.padlock_enums import EventResult, PadlockEvent
from utils.console import console_lock_out

fail_count = 0

def publish_lockout(client, generator: LockData, vault_id: str) -> None:
    lockout = generator.generate_lock_data().to_json()
    if lockout:
        topic = f"vault/padlock/{vault_id}"
        client.publish(topic, lockout)
        console_lock_out()

def detection_login_attempts(msg) -> str | None:
    global fail_count                    
    try:
        if (msg.topic) != Topics.event:
            return None                             
        data = json.loads(msg.payload.decode()) 
        payload = VaultPadlockEvents.from_dict(data)
        if payload.event == PadlockEvent.access_attempt and payload.result == EventResult.fail:
            if fail_count > 3:
                return payload.id
            else:
                fail_count += 1
        else:
            return None
    except Exception as error:
        print(f"Error processing message: {error}. topic: {msg.topic}")
        return None