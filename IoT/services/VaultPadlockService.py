from __future__ import annotations

from typing import TYPE_CHECKING
import threading
import subprocess
from pathlib import Path
import json
import sys
import time
from datetime import datetime, timezone
from utils.signal_utils import shutdown_flag
from schemas.padlock_enums import PadlockEvent, EventResult, LockState
from schemas.constants import TOPICS

if TYPE_CHECKING:
    from app.VaultPadlock import MQTTPadlockApp
    from app.ble_device import BLEDevice


class VaultPadlockService():
    @staticmethod
    def BLE(app: MQTTPadlockApp) -> None:
        ble_cmd_dir = Path(__file__).resolve().parents[2] / "BLE" / "cmd"
        app.ble_present = False
        app.ble_proc = subprocess.Popen(
            ["go", "run", "./main.go", "detect"],
            cwd=ble_cmd_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
        )
        def _stdout_reader(ble_proc: subprocess.Popen, ble_device: BLEDevice) -> None: 
            assert ble_proc.stdout is not None
            for line in ble_proc.stdout:
                line = line.strip()
                if not line:
                    continue
            
                try:
                    event = json.loads(line)
                except json.JSONDecodeError:
                    continue

                if "Present" in event:
                        app.ble_present = bool(event["Present"])
                        # print(event)
                if "LocalName" in event:
                        ble_device.local_name = event.get('LocalName')
                        ble_device.token = event.get('Token')
                        ble_device.UUID = event.get('DeviceUUID')
                        print(ble_device)
        
        def _stderr_reader(ble_proc: subprocess.Popen) -> None:
            assert ble_proc.stderr is not None
            for line in ble_proc.stderr:
                line = line.strip()
                if line:
                    print("BLE stderr:", line)

        threading.Thread(target=_stdout_reader, args=(app.ble_proc, app.ble_device), daemon=True).start()
        threading.Thread(target=_stderr_reader, args=(app.ble_proc,), daemon=True).start()

    @staticmethod
    def cli_access(app: MQTTPadlockApp):
        threading.Thread(target=_cli_access_loop, args=(app,), daemon=True,).start()


def _cli_access_loop(app: MQTTPadlockApp) -> None:
    last_state = None

    while not shutdown_flag.is_set():
        if app.ble_present != last_state:
            status = "BLE present - enter passcode" if app.ble_present else "BLE absent - waiting"
            sys.stdout.write(f"\r{status}                    \n")
            sys.stdout.flush()
            last_state = app.ble_present

        if not app.ble_present:
            time.sleep(0.2)
            continue

        code = input("Enter passcode: ").strip()
        if app.data.status_data.state == LockState.indefinite:
            break

        if not app.ble_present:
            print("Access denied: BLE no longer present")
            app.data.metric_data.unlock_attempts += 1
            _access_attempt_data(app, event=PadlockEvent.access_attempt, result=EventResult.fail)
            continue

        if code != app.passcode:
            print("Access denied: incorrect passcode")
            app.data.metric_data.unlock_attempts += 1
            _access_attempt_data(app, event=PadlockEvent.access_attempt, result=EventResult.fail)
            continue

        if code == app.passcode and app.ble_present:
            print("Access granted")
            app.data.status_data.last_unlock = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S")
            app.data.status_data.state = LockState.unlocked
            _access_attempt_data(app, event=PadlockEvent.access_attempt, result=EventResult.success)
            continue

def _access_attempt_data(app: MQTTPadlockApp, event: str, result: str):
    event_data = app.data.generate_event_data(event=event, result=result)
    if event_data is not None:
        app.client.publish(TOPICS.event, event_data)

        


