import threading
import time
import requests
from auth.config import settings

GRAFANA_URL = settings.GRAFANA_URL
GRAFANA_DS_UID = settings.GRAFANA_DS_UID
GRAFANA_USER = settings.GRAFANA_USER
GRAFANA_PASSWORD = settings.GRAFANA_PASSWORD


class GrafanaTokenRefreshService:
    def __init__(self):
        self.token: str | None = None
        self.refresh_token: str | None = None
        self.token_expires_at: float | None = None
        self.grafana_token: str | None = None
        self._refresh_thread: threading.Thread | None = None
        self._stop_refresh: threading.Event = threading.Event()
    

    def start_token_refresh_loop(self) -> None:
        if self._refresh_thread and self._refresh_thread.is_alive():
            return
        
        self._stop_refresh.clear()
        self._refresh_thread = threading.Thread(target=self._token_refresh_loop, daemon=True)
        self._refresh_thread.start()


    def stop_token_refresh_loop(self) -> None:
        self._stop_refresh.set()
        if self._refresh_thread:
            self._refresh_thread.join(timeout=5)
    

    def _token_refresh_loop(self) -> None:
        REFRESH_BUFFER = 300 # Refresh 5 minutes before expiry
        
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
                self._stop_refresh.wait(timeout=30)
                print(f"Token refresh error: {e}")
    
    
    def _ensure_valid_token(self) -> None:
        if self.token and not self._is_token_expired():
            return
        
        try:
            if self.refresh_token and self._is_token_expired():
                self.token, self.refresh_token, self.token_expires_at = self._refresh_token()
                self._configure_datasource()
        except Exception as e:
            print(f"Failed to ensure valid token: {e}")
            raise


    def _refresh_token(self) -> tuple[str, str, float]:
        response = requests.post(
            "http://localhost:8000/api/auth/token/refresh",
            headers={"X-Refresh-Token": self.refresh_token},
            timeout=10,
        )
        response.raise_for_status()
        data = response.json()
        
        token = data["access_token"]["token"]
        refresh_token = data["refresh_token"]["token"]
        token_expires_at = time.time() + data["access_token"]["expires_in"]
        return token, refresh_token, token_expires_at


    def _is_token_expired(self) -> bool:
        if not self.token_expires_at:
            return True
        return time.time() > (self.token_expires_at - 300)  #300


    def _configure_datasource(self) -> None:
        url = f"{GRAFANA_URL}/api/datasources/uid/{GRAFANA_DS_UID}"
        headers = {
            "Authorization": f"Bearer {self.grafana_token}",
            "Content-Type": "application/json",
        }

        r = requests.get(url=url, headers=headers, timeout=5)
        r.raise_for_status()
        data = r.json()
        data['secureJsonData'] = {"bearerToken": self.token}
        
        # remove read-only fields
        for field in ["version", "readOnly", "apiVersion", "typeLogoUrl"]:
            data.pop(field, None)

        r = requests.put(url=url, headers=headers, json=data, timeout=5)
        r.raise_for_status()
    