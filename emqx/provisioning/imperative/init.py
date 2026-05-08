import requests
import json
import time
import os
from pathlib import Path
from dotenv import load_dotenv
# ===================================================================================================================
### Deprecated: Using base.hocon and volume mounts for configuration instead of API provisioning.
### Keeping this file for reference and potential future use, but it's no longer part of the provisioning process.
### Was used in 'init.py' to programmatically configure EMQX via API calls.
# ===================================================================================================================

load_dotenv(Path(__file__).resolve().parent / ".env")

BASE_DIR = Path(__file__).parent
BASE_URL = os.getenv("EMQX_URL")
USER = os.getenv("ADMIN_USER")
PASS = os.getenv("ADMIN_PASS")

session = requests.Session()

def post(path, payload):
    print(f"Configuring {path}...")
    url = f"{BASE_URL}/{path}"

    try:
        response = session.post(url, json=payload, timeout=10)
        # Success
        if response.status_code in (200, 201, 204):
            print(f"Successfully configured {path}")
            return
        # Handle "already exists"
        if response.status_code in (400, 409):
            try:
                err = response.json()
                code = err.get("code", "")
                msg = err.get("message", "")
            except ValueError:
                code = ""
                msg = ""
            if code == "ALREADY_EXISTS":
                print(f"{msg}. Continuing...")
                return

        print(f"Error on {path}: {response.status_code} - {response.text}")
        response.raise_for_status()

    except requests.exceptions.RequestException as e:
        print(f"Request failed for {path}: {e}")
        raise

def post_rules(path, payload):
    print(f"Configuring {path}...")
    url = f"{BASE_URL}/{path}"

    try:
        response = session.get(url, timeout=10)
        response.raise_for_status()
        existing_rules = response.json().get("data", [])
        existing_names = {rule["name"] for rule in existing_rules}

        if payload["name"] in existing_names:
            print(f"Rule '{payload['name']}' already exists. Continuing...")
            return

        # Create new rule
        response = session.post(url, json=payload, timeout=10)
        if response.status_code in (200, 201, 204):
            print(f"Successfully configured {path}")
            return
        else:
            print(f"Error on {path}: {response.status_code} - {response.text}")
            response.raise_for_status()

    except requests.exceptions.RequestException as e:
        print(f"Request failed for {path}: {e}")
        raise

def login():
    url = f"{BASE_URL}/login"
    print(f"Attempting to login to {url}...")
    
    max_retries = 5
    for i in range(max_retries):
        try:
            r = requests.post(url, json={"username": USER, "password": PASS}, timeout=5)
            r.raise_for_status()
            token = r.json().get("token")
            print("Login successful. Token retrieved.")
            
            session.headers.update({"Authorization": f"Bearer {token}"})
            return
        except (requests.exceptions.ConnectionError, requests.exceptions.HTTPError) as e:
            if i < max_retries - 1:
                print(f"EMQX API not ready (Attempt {i+1}/{max_retries}). Retrying in 5s...")
                time.sleep(5)
            else:
                print("Could not connect to EMQX API.")
                raise e

def load(p):
    """Loads JSON from file and handles payload_template stringification."""
    file_path = BASE_DIR / p
    with open(file_path, "r") as f:
        data = json.load(f)
        
        # EMQX specific: parameters.payload_template must often be a stringified JSON
        if "parameters" in data and "payload_template" in data["parameters"]:
            template = data["parameters"]["payload_template"]
            if isinstance(template, dict):
                data["parameters"]["payload_template"] = json.dumps(template)
        return data

if __name__ == "__main__":
    try:
        login()

        provisioning_steps_1 = [
            ("authentication", "config/auth.json"),
            ("authentication/password_based:built_in_database/users", "config/device-user.json"),
            
            ("connectors", "config/mongo-connector.json"),

            ("actions", "config/action-metrics.json"),
            ("actions", "config/action-event.json"),
            ("actions", "config/action-status.json"),
        ]
        
        # 'rules' don't follow existing post pattern, so handle separately to check for existing rules and avoid duplicates
        provisioning_steps_2 = [
            ("rules", "config/rule-metrics.json"),
            ("rules", "config/rule-event.json"),
            ("rules", "config/rule-status.json"),
        ]

        for endpoint, file_path in provisioning_steps_1:
            payload = load(file_path)
            post(endpoint, payload)
        
        for endpoint, file_path in provisioning_steps_2:
            payload = load(file_path)
            post_rules(endpoint, payload)

        print(f"\nEMQX provisioning complete.")
    finally:
        session.close()