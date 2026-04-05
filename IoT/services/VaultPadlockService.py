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
from lock.lock_mechanism import detect_lock_mechanism, lock
from schemas.padlock_enums import PadlockEvent, EventResult, LockState, BleDevice
from schemas.constants import Topics
from schemas.models import TokenRequest, BleData

if TYPE_CHECKING:
    from app.VaultPadlock import MQTTPadlockApp
    from app.ble_device import BLEDevice
    from data.padlock_data_gen import StatusData


class VaultPadlockService():
    @staticmethod
    def BLE(app: MQTTPadlockApp) -> None:
        # 'register' == No BLE data, will register and return BLE data in subprocess.
        # 'detect' == BLE data already exists, will skip registration and go to listening & detect state. 
        cmd_arg = "register"
        if (app.ble_device.local_name is not None
            and app.ble_device.UUID is not None
            and app.ble_device.token is not None
        ):
            cmd_arg = "detect"

        # Start BLE subprocess for BLE bluetooth operation 
        ble_cmd_dir = Path(__file__).resolve().parents[2] / "BLE" 
        app.ble_present = False
        app.ble_proc = subprocess.Popen(
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
            app.ble_proc.stdin.write(json.dumps({
                "DeviceUUID": app.ble_device.UUID,
                "LocalName": app.ble_device.local_name,
                "Token": app.ble_device.token
            }) + "\n")
            app.ble_proc.stdin.flush()

        # stdout read from subprocess to get BLE presense 
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
                
                if BleDevice.present in event:
                        app.ble_present = bool(event["Present"])
                if BleDevice.localname in event:
                        ble_device.local_name = event.get(BleDevice.localname)
                        ble_device.token = event.get(BleDevice.token)
                        ble_device.UUID = event.get(BleDevice.deviceUUID)
                        _store_ble_data(app, ble_device)

        def _stderr_reader(ble_proc: subprocess.Popen) -> None:
            assert ble_proc.stderr is not None
            for line in ble_proc.stderr:
                line = line.strip()
                if line:
                    print("BLE stderr:", line)

        # 
        def _store_ble_data(app: MQTTPadlockApp, ble_device: BLEDevice) -> None:
            try:
                app.client.publish(
                    Topics.ble,
                    BleData(
                        id=app.id,
                        token=ble_device.token,
                        UUID=ble_device.UUID,
                        localname=ble_device.local_name,
                        timestamp=datetime.now(timezone.utc)
                    ).model_dump_json()
                )
            except Exception as e:
                print(f"Failed to publish token store data: {e}")
            
        threading.Thread(target=_stdout_reader, args=(app.ble_proc, app.ble_device), daemon=True).start()
        threading.Thread(target=_stderr_reader, args=(app.ble_proc,), daemon=True).start()

    @staticmethod
    def lock_mechanism(msg, host_topic: str, status_data: StatusData) -> None:
        if detect_lock_mechanism(msg, host_topic):
            lock(status_data)
        
    @staticmethod
    def cli_access(app: MQTTPadlockApp):
        threading.Thread(target=_cli_access_loop, args=(app,), daemon=True).start()

    @staticmethod
    def retrieve_token(app: MQTTPadlockApp, timeout: float = 10.0) -> None:
        token, uuid, localname = None, None, None

        def _token_handler(client, userdata, msg):
            nonlocal token, uuid, localname
            try:
                data = json.loads(msg.payload.decode())
                payload = BleData.model_validate(data)
            except (json.JSONDecodeError, ValueError):
                return

            if msg.topic != app.host_topic:
                return
            if payload.id != app.id:
                return
            if not payload.token or not payload.UUID or not payload.localname:
                return
            token = payload.token
            uuid = payload.UUID
            localname = payload.localname

        app.client.subscribe(app.host_topic)
        app.client.message_callback_add(app.host_topic, _token_handler)

        try:
            app.client.publish(
                Topics.ble,
                TokenRequest(
                    id=app.id,
                    request="token _request",
                    timestamp=datetime.now(timezone.utc)
                ).model_dump_json()
            )

            end_time = time.time() + timeout
            while time.time() < end_time:
                app.client.loop(timeout=0.2)
                if token and uuid and localname is not None:
                    break

        finally:
            app.client.message_callback_remove(app.host_topic)

        if token and uuid and localname is not None:
            app.ble_device.token = token
            app.ble_device.UUID = uuid
            app.ble_device.local_name = localname
            print(f"INFO: Retrieved token: {token}, UUID: {uuid}, local_name: {localname}")
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
        
        if app.data.status_data.state == LockState.unlocked:
            print("Vault unlocked, press Enter to lock.")
            input()
            app.data.status_data.state = LockState.locked
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
        app.client.publish(Topics.event, event_data)

        


