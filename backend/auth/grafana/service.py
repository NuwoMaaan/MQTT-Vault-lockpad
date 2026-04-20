import threading
import time
import requests
from auth.config import settings

GRAFANA_URL = settings.GRAFANA_URL
GRAFANA_DS_UID = settings.GRAFANA_DS_UID
GRAFANA_USER = settings.GRAFANA_USER
GRAFANA_PASSWORD = settings.GRAFANA_PASSWORD


class GrafanaTokenRefreshService:
    jwt: str | None = None
    refresh_jwt: str | None = None
    token_expires_at: float | None = None
    grafana_token: str | None = None

    _refresh_thread: threading.Thread | None = None
    _stop_refresh: threading.Event = threading.Event()
    
    @classmethod
    def start_token_refresh_loop(cls) -> None:
        if cls._refresh_thread and cls._refresh_thread.is_alive():
            return
        
        cls._stop_refresh.clear()
        cls._refresh_thread = threading.Thread(target=cls._token_refresh_loop,daemon=True)
        cls._refresh_thread.start()

    @classmethod
    def stop_token_refresh_loop(cls) -> None:
        cls._stop_refresh.set()
        if cls._refresh_thread:
            cls._refresh_thread.join(timeout=5)
    
    @classmethod
    def _token_refresh_loop(cls) -> None:
        REFRESH_BUFFER = 300  # Refresh 5 minutes before expiry
        
        while not cls._stop_refresh.is_set():
            try:
                if cls.token_expires_at is None:
                    cls._stop_refresh.wait(timeout=5)
                    continue
                
                time_until_expiry = cls.token_expires_at - time.time()
                
                if time_until_expiry <= REFRESH_BUFFER:
                    cls._ensure_valid_token()
                    time_until_expiry = cls.token_expires_at - time.time()
                
                # Sleep until next refresh is needed
                sleep_time = max(1, time_until_expiry - REFRESH_BUFFER)
                cls._stop_refresh.wait(timeout=sleep_time)
                
            except Exception as e:
                cls._stop_refresh.wait(timeout=30)
                print(f"Token refresh error: {e}")
    
    
    @classmethod
    def _ensure_valid_token(cls) -> None:
        if cls.jwt and not _is_token_expired(cls.token_expires_at):
            return
        
        try:
            if cls.refresh_jwt and _is_token_expired(cls.token_expires_at):
                cls.jwt, cls.refresh_jwt, cls.token_expires_at = _refresh_token(cls.refresh_jwt)
                _configure_datasource(cls.jwt, cls.grafana_token)
        except Exception as e:
            print(f"Failed to ensure valid token: {e}")
            raise


def _refresh_token(refresh_jwt: str) -> tuple[str, str, float]:
    response = requests.post(
        "http://localhost:8000/api/auth/token/refresh",
        headers={"X-Refresh-Token": refresh_jwt},
        timeout=10,
    )
    response.raise_for_status()
    data = response.json()
    
    jwt_token = data["access_token"]["token"]
    refresh_jwt = data["refresh_token"]["token"]
    token_expires_at = time.time() + data["access_token"]["expires_in"]
    return jwt_token, refresh_jwt, token_expires_at

def _is_token_expired(token_expires_at: float | None) -> bool:
    if not token_expires_at:
        return True
    return time.time() > (token_expires_at - 300)  #300

def _configure_datasource(token: str, grafana_token: str) -> None:
    url = f"{GRAFANA_URL}/api/datasources/uid/{GRAFANA_DS_UID}"
    headers = {
        "Authorization": f"Bearer {grafana_token}",
        "Content-Type": "application/json",
    }

    r = requests.get(url=url, headers=headers, timeout=5)
    r.raise_for_status()
    data = r.json()
    data['secureJsonData'] = {"bearerToken": token}
    
    # remove read-only fields
    for field in ["version", "readOnly", "apiVersion", "typeLogoUrl"]:
        data.pop(field, None)

    r = requests.put(url=url, headers=headers, json=data, timeout=5)
    r.raise_for_status()
    