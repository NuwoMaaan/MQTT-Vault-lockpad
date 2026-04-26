import requests
from schemas.models import BleData


class BleApiClient:
    def __init__(self):
        self.url = "http://localhost:8000/api/ble/data"
        
    def get_ble_data(self, jwt: str) -> BleData | None:
        response = requests.get(
            self.url,
            headers={"Authorization": f"Bearer {jwt}"},
            timeout=10,
        )
        if response.status_code == 404:
            return None
        
        response.raise_for_status()
        return BleData(**response.json())


    def post_ble_data(self, payload: BleData, jwt: str) -> None:
        response = requests.post(
            self.url,
            headers={"Authorization": f"Bearer {jwt}"},
            json=payload.model_dump(mode="json"),
            timeout=10,
        )
        response.raise_for_status()