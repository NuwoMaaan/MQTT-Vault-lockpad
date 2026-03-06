import requests
import json
from auth.config import settings
from auth.security.token_service import issue_service_token

GRAFANA_URL = settings.GRAFANA_URL
GRAFANA_DS_UID = settings.GRAFANA_DS_UID
GRAFANA_USER = settings.GRAFANA_USER
GRAFANA_PASSWORD = settings.GRAFANA_PASSWORD

session = requests.Session()
session.auth = (GRAFANA_USER, GRAFANA_PASSWORD)
session.headers.update({"Content-Type": "application/json"})


def create_service_account() -> int:
    url = f"{GRAFANA_URL}/api/serviceaccounts"

    print("Creating service account...")
    payload = {
        "name": "admin_service_account",
        "role": "Admin",
        "isDisabled": False
    }
    r = session.post(url, json=payload)
    r.raise_for_status()
    data = r.json()
    print("Creating service account - complete")

    return data['id']


def create_service_account_token(id: int) -> str:
    url = f"{GRAFANA_URL}/api/serviceaccounts/{id}/tokens"

    print("Creating service account token...")
    payload = {
        "name": "grafana"
        #"secondsToLive": "60000"   #DEFAULT IS 0 == NON-EXPIREY
    }
    r = session.post(url, json=payload)
    r.raise_for_status()
    data = r.json()
    print("Creating service account token - complete")

    return data['key']


def configure_datasource(token):
    url = f"{GRAFANA_URL}/api/datasources/uid/{GRAFANA_DS_UID}"

    print("Configuring datasource with token")
    r = session.get(url)
    r.raise_for_status()
    data = r.json()

    data['secureJsonData'] = {"bearerToken": token}
    
    # remove read-only fields
    for field in ["version", "readOnly", "apiVersion", "typeLogoUrl"]:
        data.pop(field, None)

    r = session.put(url, json=data)
    r.raise_for_status()
    print("Grafana Datasource: Infinity bearer token updated", r.status_code)


if __name__ == "__main__":
    service_account_id = create_service_account()
    grafana_token = create_service_account_token(service_account_id)
    session.auth = None
    session.headers.update({
        "Authorization": f"Bearer {grafana_token}"
    })

    api_token = issue_service_token(service_name="GrafanaSA")
    configure_datasource(api_token)
    print("Complete Grafana Infininty datasource authorization method configuration")