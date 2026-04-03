from __future__ import annotations

import json
from typing import TYPE_CHECKING
from schemas.constants import Topics
from schemas.models import TokenRequest, BleToken
from lock.lockout import publish_lockout, detection_login_attempts
from connection.config import settings
from pydantic import ValidationError
import requests

if TYPE_CHECKING:
    from data.control_data_gen import ControlDataGenerator


class ControlComputerService:
    jwt: str | None = None

    @staticmethod
    def detection_mechanism(msg, client, data: ControlDataGenerator, lock_id: str) -> None:
        lock_id = detection_login_attempts(msg)
        if lock_id:                                 
            publish_lockout(client, data, lock_id)
    
    @classmethod
    def ble_token_handler(cls, msg) -> BleToken | None:
        if msg.topic != Topics.token:
            return
        if not cls.jwt:
            cls.jwt = _create_jwt_token(settings.API_KEY)

        try:
            data = json.loads(msg.payload.decode())
        except json.JSONDecodeError as e:
            print(f"Invalid JSON: {e}")
            return

        try:
            payload = BleToken.model_validate(data)
            _post_token(payload, cls.jwt)
            return 
        except ValidationError:
            pass

        try:
            _ = TokenRequest.model_validate(data)
            ble_token = _get_token(cls.jwt)
            return ble_token
        except ValidationError:
            pass

def _get_token(jwt: str) -> BleToken| None:
    response = requests.get(
        f"http://localhost:8000/ble/token",
        headers={"Authorization": f"Bearer {jwt}"},
        timeout=10,
    )
    response.raise_for_status()
    return BleToken(**response.json())


def _post_token(payload: BleToken, jwt: str) -> None:
    response = requests.post(
        f"http://localhost:8000/ble/token",
        headers={"Authorization": f"Bearer {jwt}"},
        json=payload.model_dump(),
        timeout=10,
    )
    response.raise_for_status()
    return None

def _create_jwt_token(api_key: str) -> str:
    response = requests.post(
        "http://localhost:8000/auth/token",
        headers={"X-API-Key": api_key},
        timeout=10,
    )
    response.raise_for_status()
    return response.json().get("access_token")

