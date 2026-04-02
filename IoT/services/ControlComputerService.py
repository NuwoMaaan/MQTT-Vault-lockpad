from __future__ import annotations

import json
from typing import TYPE_CHECKING
from schemas.constants import Topics
from schemas.models import StoreToken, TokenRequest
from lock.lockout import publish_lockout, detection_login_attempts
from pydantic import ValidationError
import requests

if TYPE_CHECKING:
    from data.control_data_gen import ControlDataGenerator

class ControlComputerService:
    @staticmethod
    def detection_mechanism(msg, client, data: ControlDataGenerator, lock_id: str) -> None:
        lock_id = detection_login_attempts(msg)
        if lock_id:                                 
            publish_lockout(client, data, lock_id)
    
    @staticmethod
    def ble_token_handler(msg) -> str | None:
        if msg.topic != Topics.token:
            return

        try:
            data = json.loads(msg.payload.decode())
        except json.JSONDecodeError as e:
            print(f"Invalid JSON: {e}")
            return

        try:
            payload = StoreToken.model_validate(data)
            _post_token(payload)
            return
        except ValidationError:
            pass

        try:
            payload = TokenRequest.model_validate(data)
            _get_token(payload)
            return
        except ValidationError:
            pass

def _get_token(payload, client):
    pass

def _post_token(payload, client):
    pass
