from __future__ import annotations

import threading
from typing import TYPE_CHECKING
from schemas.constants import Topics
import sys
import time
from datetime import datetime, timezone
from schemas.padlock_enums import PadlockEvent, EventResult, LockState
from utils.signal_utils import shutdown_flag

if TYPE_CHECKING:
    from data.padlock_data_gen import PadlockDataGenerator
    from services.vault_padlock.BLEDevice import BLEDevice
    from paho.mqtt import client as mqtt_client


class CLIService():
    def __init__(self, ble_device: BLEDevice, data: PadlockDataGenerator):
        self.ble_device = ble_device
        self.data = data
    
    def cli_access(self, client: mqtt_client, passcode: str) -> None:
        threading.Thread(target=self._cli_access_loop, args=(client, passcode), daemon=True).start()

    def _cli_access_loop(self, client: mqtt_client, passcode: str) -> None:
        last_state = None

        while not shutdown_flag.is_set():
            if self.ble_device.ble_present != last_state:
                status = "BLE present - enter passcode" if self.ble_device.ble_present else "BLE absent - waiting"
                sys.stdout.write(f"\r{status}                    \n")
                sys.stdout.flush()
                last_state = self.ble_device.ble_present

            if not self.ble_device.ble_present:
                time.sleep(0.2)
                continue
            
            if self.data.status_data.state == LockState.unlocked:
                print("Vault unlocked, press Enter to lock.")
                input()
                self.data.status_data.state = LockState.locked
                continue

            code = input("Enter passcode: ").strip()
            if self.data.status_data.state == LockState.indefinite:
                break
        
            if not self.ble_device.ble_present:
                print("Access denied: BLE no longer present")
                self.data.metric_data.unlock_attempts += 1
                self._access_attempt_data(client, event=PadlockEvent.access_attempt, result=EventResult.fail)
                continue

            if code != passcode:
                print("Access denied: incorrect passcode")
                self.data.metric_data.unlock_attempts += 1
                self._access_attempt_data(client, event=PadlockEvent.access_attempt, result=EventResult.fail)
                continue

            if code == passcode and self.ble_device.ble_present:
                print("Access granted")
                self.data.status_data.last_unlock = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S")
                self.data.status_data.state = LockState.unlocked
                self._access_attempt_data(client, event=PadlockEvent.access_attempt, result=EventResult.success)
                continue


    def _access_attempt_data(self, client: mqtt_client, event: str, result: str):
        event_data = self.data.generate_event_data(event=event, result=result)
        if event_data is not None:
            client.publish(Topics.event, event_data)