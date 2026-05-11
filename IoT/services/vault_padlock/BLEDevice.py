from __future__ import annotations

from typing import TYPE_CHECKING
from datetime import datetime, timezone
from pathlib import Path
import threading
import subprocess
import json
from schemas.constants import Topics
from schemas.models import BleData
from schemas.padlock_enums import BleDevice
if TYPE_CHECKING:
    from paho.mqtt import client as mqtt_client


class BLEDevice():
    def __init__(self):
        self.UUID = None
        self.token = None
        self.local_name = None
        self.ble_present = False
        self.ble_proc = None

    def __repr__(self):
        return f"<BLEDevice(localname='{self.local_name}', UUID='{self.UUID}', token='{self.token}')>"
    
    def BLE(self, client: mqtt_client, app_id: str) -> None:
        # 'register' == No BLE data, will register and return BLE data in subprocess.
        # 'detect' == BLE data already exists, will skip registration and go to listening & detect state. 
        cmd_arg = "register"
        if (self.local_name is not None
            and self.UUID is not None
            and self.token is not None
        ):
            cmd_arg = "detect"

        # Start BLE subprocess for BLE bluetooth operation 
        ble_cmd_dir = Path(__file__).resolve().parents[3] / "BLE" 
        self.ble_present = False
        self.ble_proc = subprocess.Popen(
            ["go", "run", "cmd/main.go", cmd_arg],
            cwd=ble_cmd_dir,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
        )
        
        # stdin write to subprocess BLE data
        if cmd_arg == "detect":
            self.ble_proc.stdin.write(json.dumps({
                "DeviceUUID": self.UUID,
                "LocalName": self.local_name,
                "Token": self.token
            }) + "\n")
            self.ble_proc.stdin.flush()
        
        threading.Thread(target=self._stdout_reader, args=(client, app_id,), daemon=True).start()
        threading.Thread(target=self._stderr_reader, daemon=True).start()

    # stdout read from subprocess to get BLE presense 
    def _stdout_reader(self, client: mqtt_client, app_id: str) -> None: 
        assert self.ble_proc.stdout is not None
        for line in self.ble_proc.stdout:
            line = line.strip()
            if not line:
                continue
        
            try:
                event = json.loads(line)
            except json.JSONDecodeError:
                continue
            
            if BleDevice.present in event:
                    self.ble_present = bool(event["Present"])
            if BleDevice.localname in event:
                    self.local_name = event.get(BleDevice.localname)
                    self.token = event.get(BleDevice.token)
                    self.UUID = event.get(BleDevice.deviceUUID)
                    self._store_ble_data(client, app_id)

    def _stderr_reader(self) -> None:
        assert self.ble_proc.stderr is not None
        for line in self.ble_proc.stderr:
            line = line.strip()
            if line:
                print("BLE stderr:", line)
    
    def _store_ble_data(self, client: mqtt_client, app_id: str) -> None:
        try:
            client.publish(
                Topics.ble,
                BleData(
                    id=app_id,
                    token=self.token,
                    UUID=self.UUID,
                    localname=self.local_name,
                    timestamp=datetime.now(timezone.utc)
                ).to_json()
            )
        except Exception as e:
            print(f"Failed to publish token store data: {e}")
            
