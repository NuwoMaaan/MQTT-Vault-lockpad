from __future__ import annotations

import json
import threading
import time
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
    refresh_jwt: str | None = None
    token_expires_at: float | None = None
    _refresh_thread: threading.Thread | None = None
    _stop_refresh: threading.Event = threading.Event()

    @staticmethod
    def detection_mechanism(msg, client, data: LockData, lock_id: str) -> None:
        lock_id = detection_login_attempts(msg)
        if lock_id:                                 
            publish_lockout(client, data, lock_id)
    
    @classmethod
    def start_token_refresh_loop(cls) -> None:
        if cls._refresh_thread and cls._refresh_thread.is_alive():
            return
        
        cls._stop_refresh.clear()
        cls._refresh_thread = threading.Thread(target=cls._token_refresh_loop, daemon=True)
        cls._refresh_thread.start()
    
    @classmethod
    def _token_refresh_loop(cls) -> None:
        REFRESH_BUFFER = 300  # Refresh 5 minutes before expiry
        
        while not cls._stop_refresh.is_set():
            try:
                if cls.token_expires_at is None:
                    cls._stop_refresh.wait(timeout=5)
                    continue
                
                time_until_expiry = cls.token_expires_at - time.time()
                
                if time_until_expiry <= REFRESH_BUFFER:
                    cls._ensure_valid_token()
                    time_until_expiry = cls.token_expires_at - time.time()
                
                # Sleep until next refresh is needed (e.g. 5 min before expiry)
                sleep_time = max(1, time_until_expiry - REFRESH_BUFFER)
                cls._stop_refresh.wait(timeout=sleep_time)
                
            except Exception as e:
                print(f"Token refresh loop error: {e}")
                cls._stop_refresh.wait(timeout=30)

    @classmethod
    def ble_data_handler(cls, msg, client) -> None:
        if msg.topic != Topics.ble:
            return
        
        if not cls.jwt:
            cls._ensure_valid_token()

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

    @classmethod
    def _ensure_valid_token(cls) -> None:
        if cls.jwt and not _is_token_expired(cls.token_expires_at):
            return
        
        try:
            if cls.refresh_jwt and not _is_token_expired(cls.token_expires_at):
                # Refresh token exists and is valid, use it
                cls.jwt, cls.refresh_jwt, cls.token_expires_at = _refresh_token(cls.refresh_jwt)
            else:
                cls.jwt, cls.refresh_jwt, cls.token_expires_at = _create_jwt_token(settings.API_KEY)
        except Exception as e:
            print(f"Failed to ensure valid token: {e}")
            raise


# Send BLE data if any, back to padlock
def _transport_ble(ble_data: BleData, client, vault_id: str) -> None:
    topic = f"vault/padlock/{vault_id}"
    ble_data_json = ble_data.model_dump_json()
    client.publish(topic, ble_data_json)


def _get_ble_data(jwt: str) -> BleData | None:
    response = requests.get(
        f"http://localhost:8000/api/ble/data",
        headers={"Authorization": f"Bearer {jwt}"},
        timeout=10,
    )
    if response.status_code == 404:
        return None
    
    response.raise_for_status()
    return BleData(**response.json())


def _post_ble_data(payload: BleData, jwt: str) -> None:
    response = requests.post(
        f"http://localhost:8000/api/ble/data",
        headers={"Authorization": f"Bearer {jwt}"},
        json=payload.model_dump(mode="json"),
        timeout=10,
    )
    response.raise_for_status()


def _create_jwt_token(api_key: str) -> tuple[str, str, float]:
    response = requests.post(
        "http://localhost:8000/api/auth/ble/token", 
        headers={
            "X-API-Key": api_key,
            "X-Service-Name": "ControlComputerService"
        },
        timeout=10,
    )
    response.raise_for_status()
    response_data = response.json()

    jwt_token = response_data['access_token']['token']
    refresh_jwt_token = response_data['refresh_token']['token']
    token_expires_at = time.time() + response_data['access_token']['expires_in']
    return jwt_token, refresh_jwt_token, token_expires_at


def _refresh_token(refresh_jwt_token: str) -> tuple[str, str, float]:
    """Refresh using existing refresh token"""
    response = requests.post(
        "http://localhost:8000/api/auth/token/refresh",
        headers={"X-Refresh-Token": refresh_jwt_token},
        timeout=10,
    )
    response.raise_for_status()
    data = response.json()
    
    jwt_token = data["access_token"]["token"]
    refresh_jwt_token = data["refresh_token"]["token"]
    token_expires_at = time.time() + data["access_token"]["expires_in"]
    return jwt_token, refresh_jwt_token, token_expires_at


def _is_token_expired(token_expires_at: float | None) -> bool:
    if not token_expires_at:
        return True
    return time.time() > (token_expires_at - 300)  # 5 min buffer