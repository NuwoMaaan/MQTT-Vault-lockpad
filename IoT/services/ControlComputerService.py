from __future__ import annotations

import json
from typing import TYPE_CHECKING
from schemas.constants import Topics
from schemas.models import BleDataRequest, BleData
from lock.lockout import publish_lockout, detection_login_attempts
from connection.config import settings
from pydantic import ValidationError
import requests

if TYPE_CHECKING:
    from data.control_data_gen import LockData


class ControlComputerService:
    jwt: str | None = None

    @staticmethod
    def detection_mechanism(msg, client, data: LockData, lock_id: str) -> None:
        lock_id = detection_login_attempts(msg)
        if lock_id:                                 
            publish_lockout(client, data, lock_id)
    
    @classmethod
    def ble_data_handler(cls, msg, client) -> None:
        if msg.topic != Topics.ble:
            return
        if not cls.jwt:
            cls.jwt = _create_jwt_token(settings.API_KEY)

        try:
            data = json.loads(msg.payload.decode())
        except json.JSONDecodeError as e:
            print(f"Invalid JSON: {e}")
            return

        try:
            payload = BleData.model_validate(data)
            _post_ble_data(payload, cls.jwt)
            return 
        except ValidationError:
            pass
        
        try:
            payload = BleDataRequest.model_validate(data)
            ble_data = _get_ble_data(cls.jwt)
            if ble_data:
                _transport_ble(ble_data, client, payload.id)
            else:
                print("no ble data found for request")
        except ValidationError:
            pass

# Send BLE data if any, back to padlock
def _transport_ble(ble_data: BleData, client, vault_id: str) -> None:
    topic = f"vault/padlock/{vault_id}"
    ble_data_json = ble_data.model_dump_json()
    client.publish(topic, ble_data_json)


def _get_ble_data(jwt: str) -> BleData| None:
    response = requests.get(
        f"http://localhost:8000/api/ble/token",
        headers={"Authorization": f"Bearer {jwt}"},
        timeout=10,
    )
    if response.status_code == 404:
        return None
    
    response.raise_for_status()
    return BleData(**response.json())


def _post_ble_data(payload: BleData, jwt: str) -> None:
    response = requests.post(
        f"http://localhost:8000/api/ble/token",
        headers={"Authorization": f"Bearer {jwt}"},
        json=payload.model_dump(mode="json"),
        timeout=10,
    )
    response.raise_for_status()
    return None


def _create_jwt_token(api_key: str) -> str:
    response = requests.post(
        "http://localhost:8000/api/auth/token",
        headers={
            "X-API-Key": api_key,
            "X-Service-Name": "ControlComputerService"
        },
        timeout=10,
    )
    response.raise_for_status()
    return response.json().get("access_token")

