from __future__ import annotations

from typing import TYPE_CHECKING
import threading
import subprocess
from pathlib import Path
import json

if TYPE_CHECKING:
    from app.VaultPadlock import MQTTPadlockApp
    from app.ble_device import BLEDevice


class VaultPadlockService():
    @staticmethod
    def detect_BLE_device(app: MQTTPadlockApp) -> None:
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
        def stdout_reader(ble_proc: subprocess.Popen, ble_device: BLEDevice) -> None: 
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
                        print(event)
                if "LocalName" in event:
                        ble_device.local_name = event.get('LocalName')
                        ble_device.token = event.get('Token')
                        ble_device.UUID = event.get('DeviceUUID')
                        print(ble_device)
        

        def stderr_reader(ble_proc: subprocess.Popen) -> None:
            assert ble_proc.stderr is not None
            for line in ble_proc.stderr:
                line = line.strip()
                if line:
                    print("BLE stderr:", line)

        threading.Thread(target=stdout_reader, args=(app.ble_proc, app.ble_device), daemon=True).start()
        threading.Thread(target=stderr_reader, args=(app.ble_proc,), daemon=True).start()


    @staticmethod
    def detect_ble_present():
        pass

    @staticmethod
    def access_attempt():
        pass

    @staticmethod
    def get_token():
        pass