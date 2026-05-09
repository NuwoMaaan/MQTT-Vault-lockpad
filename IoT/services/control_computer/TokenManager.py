import threading
import time
import requests
from connection.config import settings


class TokenManager:
    def __init__(self):
        self.token: str | None = None
        self.refresh_token: str | None = None
        self.token_expires_at: float | None = None
        self._refresh_thread: threading.Thread | None = None
        self._stop_refresh: threading.Event = threading.Event()


    def get_token(self) -> str:
        if not self.token or self._is_token_expired():
            self._ensure_valid_token()
        return self.token
       

    def start_token_refresh_loop(self) -> None:
        if self._refresh_thread and self._refresh_thread.is_alive():
            return
        
        self._stop_refresh.clear()
        self._refresh_thread = threading.Thread(target=self._token_refresh_loop, daemon=True)
        self._refresh_thread.start()

     
    def _token_refresh_loop(self) -> None:
        REFRESH_BUFFER = 300  # Refresh 5 minutes before expiry (300)
        
        while not self._stop_refresh.is_set():
            try:
                if self.token_expires_at is None:
                    self._stop_refresh.wait(timeout=5)
                    continue
                
                time_until_expiry = self.token_expires_at - time.time()
                
                if time_until_expiry <= REFRESH_BUFFER:
                    self._ensure_valid_token()
                    time_until_expiry = self.token_expires_at - time.time()
                
                # Sleep until next refresh is needed
                sleep_time = max(1, time_until_expiry - REFRESH_BUFFER)
                self._stop_refresh.wait(timeout=sleep_time)
                
            except Exception as e:
                print(f"Token refresh loop error: {e}")
                self._stop_refresh.wait(timeout=30)
       

    def _ensure_valid_token(self) -> None:
        if self.token and not self._is_token_expired():
            return
        
        try:
            if self.refresh_token and self._is_token_expired():
                self.token, self.refresh_token, self.token_expires_at = self._refresh_token(self.refresh_token)
            else:
                self.token, self.refresh_token, self.token_expires_at = self._create_jwt_token(settings.API_KEY)
        except Exception as e:
            print(f"Failed to ensure valid token: {e}")
            raise
    

    def _is_token_expired(self) -> bool:
        if not self.token_expires_at:
            return True
        return time.time() > (self.token_expires_at - 300)  #300


    def _request_token(self, url: str, headers: dict) -> tuple[str, str, float]:
        response = requests.post(url, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()

        token = data["access_token"]["token"]
        refresh_token = data["refresh_token"]["token"]
        token_expires_at = time.time() + data["access_token"]["expires_in"]
        return token, refresh_token, token_expires_at


    def _create_jwt_token(self, api_key: str) -> tuple[str, str, float]:
        return self._request_token(
            url="http://localhost:8000/api/auth/ble/token",
            headers={
                "X-API-Key": api_key,
                "X-Service-Name": "ControlComputerService"
            }
        )


    def _refresh_token(self, refresh_token: str) -> tuple[str, str, float]:
        return self._request_token(
            url="http://localhost:8000/api/auth/token/refresh",
            headers={"X-Refresh-Token": refresh_token}
        )
        