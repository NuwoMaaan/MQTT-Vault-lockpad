import requests
import json

from connections.config import settings
from pathlib import Path

BASE_DIR = Path(__file__).parent

BASE_URL = settings.EMQX_URL
USER = settings.USER
PASS = settings.PASS

def post(token, path, payload):
    print(f"Configuring {path}")
    r = requests.post(
        BASE_URL + path,
        headers={"Authorization": f"Bearer {token}"},
        json=payload  
    )
    if r.status_code not in (200, 201, 204):
        print(path, r.status_code, r.text)
        r.raise_for_status()

def login():
    print("Retrieving auth token...")
    r = requests.post(
        BASE_URL + "/login",
        json={"username": USER, "password": PASS}
    )
    r.raise_for_status()
    return r.json()["token"]

def load(p):
    with open(BASE_DIR / p, "r") as f:
        data = json.load(f)
        # Check if payload_template is a dict and stringify it
        if "parameters" in data and "payload_template" in data["parameters"]:
            template = data["parameters"]["payload_template"]
            if isinstance(template, dict):
                data["parameters"]["payload_template"] = json.dumps(template)
        return data

if __name__ == "__main__":

    #time.sleep(10)

    token = login()

    # 1. MQTT authentication backend
    post(token, "/authentication", load("provisioning/auth.json"))

    # 2. MQTT device user
    post(
        token,
        "/authentication/password_based:built_in_database/users",
        load("provisioning/device-user.json")
    )

    # 3. Mongo connector
    post(token, "/connectors", load("provisioning/mongo-connector.json"))

    # 4. Actions
    post(token, "/actions", load("provisioning/action-metrics.json"))
    post(token, "/actions", load("provisioning/action-event.json"))
    post(token, "/actions", load("provisioning/action-status.json"))

    # 5. Rules
    post(token, "/rules", load("provisioning/rule-metrics.json"))
    post(token, "/rules", load("provisioning/rule-event.json"))
    post(token, "/rules", load("provisioning/rule-status.json"))

    print("EMQX provisioning finished.")