from __future__ import annotations

from typing import TYPE_CHECKING
from lock.lock_mechanism import detect_lock_mechanism, lock
from data.padlock_data_gen import PadlockDataGenerator
from services.vault_padlock.CLIService import CLIService
from services.vault_padlock.BLEDevice import BLEDevice
from services.vault_padlock.BLEData import BLEData

if TYPE_CHECKING:
    from paho.mqtt import client as mqtt_client
    from data.padlock_data_gen import StatusData


class VaultPadlockService():
    def __init__(self, id: str):
        self.app_id = id
        self.ble_device = BLEDevice()
        self.app_data = PadlockDataGenerator(id)
        self.cli_service = CLIService(self.ble_device, self.app_data)
        self.ble_data = BLEData(self.ble_device)
    

    def start_ble(self, client: mqtt_client) -> None:
        self.ble_device.BLE(client, self.app_id)


    def lock_mechanism(self, msg, host_topic: str, status_data: StatusData) -> None:
        if detect_lock_mechanism(msg, host_topic):
            lock(status_data)
        

    def cli_access(self, client: mqtt_client, passcode: str) -> None:
        self.cli_service.cli_access(client, passcode)
    

    def retrieve_ble_data(self, client: mqtt_client, host_topic: str, timeout: float = 5.0) -> None:
        self.ble_data.retrieve_ble_data(client, self.app_id, host_topic, timeout)

    