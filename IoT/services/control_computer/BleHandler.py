from __future__ import annotations

from typing import TYPE_CHECKING
import json
from pydantic import ValidationError
from schemas.models import BleData, BleDataRequest
from schemas.constants import Topics

if TYPE_CHECKING:
    from services.control_computer.TokenManager import TokenManager
    from services.control_computer import BleApiClient
    

class BleHandler:
    def __init__(self, token_manager: TokenManager, api_client: BleApiClient):
        self.token_manager = token_manager
        self.api_client = api_client

    def data_handler(self, msg, client) -> None:
        if msg.topic != Topics.ble:
            return
         
        jwt = self.token_manager.get_token()

        try:
            data = json.loads(msg.payload.decode())
        except json.JSONDecodeError as e:
            print(f"Invalid JSON: {e}")
            return
        
        # Try BleData
        try:
            payload = BleData.from_dict(data)
            try:
                self.api_client.post_ble_data(payload, jwt)
                return
            except Exception as api_error:
                print(f"Error posting BleData: {api_error}")
                return
        except (TypeError, ValueError):
            pass
        
        # Try BleDataRequest
        try:
            payload = BleDataRequest.from_dict(data)
            ble_data = self.api_client.get_ble_data(jwt)
            if ble_data:
                self._transport_ble(ble_data, client, payload.id)
            else:
                print("no ble data found for request")
        except (TypeError, ValueError):
            pass

    def _transport_ble(self, ble_data: BleData, client, vault_id: str) -> None:
        topic = f"vault/padlock/{vault_id}"
        ble_data_json = ble_data.to_json()
        client.publish(topic, ble_data_json)