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
        self._last_ble_state = None
    

    def cli_access(self, client: mqtt_client, passcode: str) -> None:
        threading.Thread(target=self._cli_access_loop, args=(client, passcode), daemon=True).start()


    def _cli_access_loop(self, client: mqtt_client, passcode: str) -> None:
        while not shutdown_flag.is_set():
            self._handle_ble_presence()

            if not self._wait_for_ble():
                continue

            if self._handle_unlocked_state():
                continue

            code = input("Enter passcode: ").strip()

            if self.data.status_data.state == LockState.indefinite:
                break

            self._handle_access_attempt(client, passcode, code)


    def _handle_ble_presence(self) -> None:
        if self.ble_device.ble_present != self._last_ble_state:
            status = (
                "BLE present - enter passcode"
                if self.ble_device.ble_present
                else "BLE absent - waiting"
            )

            sys.stdout.write(f"\r{status}                    \n")
            sys.stdout.flush()

            self._last_ble_state = self.ble_device.ble_present


    def _wait_for_ble(self) -> bool:
        if self.ble_device.ble_present:
            return True
        time.sleep(0.2)
        return False
    

    def _handle_unlocked_state(self) -> bool:
        if self.data.status_data.state != LockState.unlocked:
            return False
        print("Vault unlocked, press Enter to lock.")
        input()

        self.data.status_data.state = LockState.locked
        return True
    

    def _handle_access_attempt(self, client: mqtt_client, expected_passcode: str, entered_code: str) -> None:
        if not self.ble_device.ble_present:
            self._access_denied(client, "BLE no longer present")
            return

        if entered_code != expected_passcode:
            self._access_denied(client, "incorrect passcode")
            return

        self._access_granted(client)


    def _access_denied(self, client: mqtt_client, reason: str) -> None:
        print(f"Access denied: {reason}")
        self.data.metric_data.unlock_attempts += 1
        self._access_attempt_data(
            client,
            event=PadlockEvent.access_attempt,
            result=EventResult.fail
        )


    def _access_granted(self, client: mqtt_client) -> None:
        print("Access granted")
        self.data.status_data.last_unlock = (datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S"))
        self.data.status_data.state = LockState.unlocked
        self._access_attempt_data(
            client,
            event=PadlockEvent.access_attempt,
            result=EventResult.success
        )


    def _access_attempt_data(self, client: mqtt_client, event: str, result: str):
        event_data = self.data.generate_event_data(event=event, result=result)
        if event_data is not None:
            client.publish(Topics.event, event_data)