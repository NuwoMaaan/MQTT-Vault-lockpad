from __future__ import annotations

from typing import TYPE_CHECKING
from services.control_computer.TokenManager import TokenManager
from services.control_computer.BleApiClient import BleApiClient
from services.control_computer.BleHandler import BleHandler
from lock.lockout import publish_lockout, detection_login_attempts

if TYPE_CHECKING:
    from data.control_data_gen import LockData


class ControlComputerService:
    def __init__(self):
        self.token_manager = TokenManager()
        self.api_client = BleApiClient()
        self.ble_handler = BleHandler(self.token_manager, self.api_client)
    
    def start_jwt_refresh_loop(self) -> None:
        self.token_manager.start_token_refresh_loop()
    
    def ble_data_handler(self, msg, client):
        self.ble_handler.data_handler(msg, client)

    def detection_mechanism(self, msg, client, data: LockData, lock_id: str) -> None:
        lock_id = detection_login_attempts(msg)
        if lock_id:                                 
            publish_lockout(client, data, lock_id)







    