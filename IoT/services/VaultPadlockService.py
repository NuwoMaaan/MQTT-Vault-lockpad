from typing import TYPE_CHECKING
import threading
import subprocess
from pathlib import Path
import json

if TYPE_CHECKING:
    from app.VaultPadlock import MQTTPadlockApp


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
        def stdout_reader() -> None: 
            assert app.ble_proc.stdout is not None
            for line in app.ble_proc.stdout:
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
                        app.ble_device.local_name = event.get('LocalName')
                        app.ble_device.token = event.get('Token')
                        app.ble_device.UUID = event.get('DeviceUUID')
                        print(app.ble_device)
        

        def stderr_reader() -> None:
            assert app.ble_proc.stderr is not None
            for line in app.ble_proc.stderr:
                line = line.strip()
                if line:
                    print("BLE stderr:", line)

        threading.Thread(target=stdout_reader, daemon=True).start()
        threading.Thread(target=stderr_reader, daemon=True).start()


    @staticmethod
    def detect_ble_present():
        pass

    @staticmethod
    def access_attempt():
        pass

    @staticmethod
    def get_token():
        pass