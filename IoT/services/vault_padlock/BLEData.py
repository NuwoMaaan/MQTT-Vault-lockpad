from __future__ import annotations

from typing import TYPE_CHECKING
import time
import sys
import json
from datetime import datetime, timezone
from utils.signal_utils import shutdown_flag
from schemas.constants import Topics
from schemas.models import BleData, BleDataRequest

if TYPE_CHECKING:
    from paho.mqtt import client as mqtt_client
    from services.vault_padlock.BLEDevice import BLEDevice

class BLEData():
    def __init__(self, ble_device: BLEDevice):
        self.ble_device = ble_device
        self.token: str = None
        self.uuid: str = None
        self.localname: str = None

        
    def retrieve_ble_data(self, client: mqtt_client, app_id: str, host_topic: str, timeout: float) -> None:
        def _token_handler(client, userdata, msg):
            try:
                data = json.loads(msg.payload.decode()) 
                payload = BleData.from_dict(data)
            except (json.JSONDecodeError, ValueError) as e:
                print(f"Error validating BleData: {e}")
                return

            if msg.topic != host_topic:
                return
            if payload.id != app_id:
                return
            if not payload.token or not payload.UUID or not payload.localname:
                return
            self.token = payload.token
            self.uuid = payload.UUID
            self.localname = payload.localname

        client.subscribe(host_topic)
        client.message_callback_add(host_topic, _token_handler)

        self._publish_request(client, app_id, host_topic, timeout)
        self._assign_ble_data()

    
    def _assign_ble_data(self) -> None:
        if self.token is not None and self.uuid is not None and self.localname is not None:
            self.ble_device.token = self.token
            self.ble_device.UUID = self.uuid
            self.ble_device.local_name = self.localname
            print(f"INFO: Retrieved token: {self.token}, UUID: {self.uuid}, local_name: {self.localname}")
            print("INFO: Sending BLE data to subprocess... (arg=detect)")
        else:
            print("INFO: Failed to retrieve BLE data within timeout")
            print("INFO: Present BLE device for new registration")
            while True:
                choice = input("INFO: y - BLE device is activated?, n - Exit program to retry (y/n): ").strip().lower()
                if choice in ['y', 'n']:
                    break

            if choice == 'n':
                print("INFO: Exiting program.")
                shutdown_flag.set()
                sys.exit(0)
    

    def _publish_request(self, client: mqtt_client, app_id: str, host_topic: str, timeout: float) -> None:
        try:
            client.publish(
                Topics.ble,
                BleDataRequest(
                    id=app_id,
                    request="ble_request",
                    timestamp=datetime.now(timezone.utc)
                ).to_json()
            )

            end_time = time.time() + timeout
            while time.time() < end_time:
                client.loop(timeout=0.2)
                if self.token is not None and self.uuid is not None and self.localname is not None:
                    break

        finally:
            client.message_callback_remove(host_topic)