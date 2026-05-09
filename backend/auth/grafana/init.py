import time
import requests
from auth.config import settings
from auth.security.token_service import issue_service_token
from auth.models.permissions import VaultScopes
from auth.grafana.service import GrafanaTokenRefreshService


GRAFANA_URL = settings.GRAFANA_URL
GRAFANA_DS_UID = settings.GRAFANA_DS_UID
GRAFANA_USER = settings.GRAFANA_USER
GRAFANA_PASSWORD = settings.GRAFANA_PASSWORD

session = requests.Session()
session.auth = (GRAFANA_USER, GRAFANA_PASSWORD)
session.headers.update({"Content-Type": "application/json"})

# Token id is required for deletion
def get_service_account_token_id(id: int) -> int:
    url = f"{GRAFANA_URL}/api/serviceaccounts/{id}/tokens"
    r = session.get(url)
    r.raise_for_status()

    return r.json()[0]['id']


# Delete token to ensure only one exists
def delete_service_account_token(sa_id: int, token_id: int) -> None:
    url = f"{GRAFANA_URL}/api/serviceaccounts/{sa_id}/tokens/{token_id}"
    r = session.delete(url)
    r.raise_for_status()
    print("Deleted existing service account token")


def get_service_account_id(name: str, url: str) -> str | None:
    url = f"{url}/search"
    r = session.get(url)
    r.raise_for_status()

    for sa in r.json()['serviceAccounts']:
        if sa['name'] == name:
            return sa['id']
    return None

def create_service_account(name: str) -> tuple[int, bool]:
    url = f"{GRAFANA_URL}/api/serviceaccounts"
    
    # Check if service account already exists
    existing_id = get_service_account_id(name, url)
    if existing_id:
        return existing_id, True

    print("Creating service account...")
    payload = {
        "name": name,
        "role": "Admin",
        "isDisabled": False
    } 
    r = session.post(url, json=payload)
    r.raise_for_status()
    data = r.json()
    print("Creating service account - complete")

    return data['id'], False


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
    print("Grafana Datasource: Infinity bearer token updated")

def init(token_manager: GrafanaTokenRefreshService):
    try:
        service_account_id, service_account_exists = create_service_account("admin_service_account")
        if service_account_exists:
            token_id = get_service_account_token_id(service_account_id)
            delete_service_account_token(service_account_id, token_id)

        grafana_token = create_service_account_token(service_account_id)
        session.auth = None
        session.headers.update({
            "Authorization": f"Bearer {grafana_token}"
        })

        token_response = issue_service_token(service_name="GrafanaSA",
                                        scopes=[
                                            VaultScopes.METRICS_READ,
                                            VaultScopes.STATUS_READ,
                                            VaultScopes.EVENTS_READ
                                        ])
        configure_datasource(token_response.access_token)
        print("Complete - Grafana Infininty datasource authorization method configuration")

        token_manager.token = token_response.access_token
        token_manager.refresh_token = token_response.refresh_token
        token_manager.token_expires_at = time.time() + token_response.access_token_expires_in
        token_manager.grafana_token = grafana_token

    finally:
        session.close()

