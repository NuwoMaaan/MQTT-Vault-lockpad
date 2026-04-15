## Overview

**MQTT** (Message Queuing Telemetry Transport) is a lightweight, publish–subscribe messaging protocol used for reliable communication between devices in distributed systems. It operates through a central broker that manages message exchange between clients, allowing devices to publish data to topics and subscribe to receive updates. This design enables efficient, real-time, and scalable communication, making MQTT widely used in IoT, automation, and remote monitoring applications.

**MQTT Vault Padlock** Is a project to demostrate MQTT communications and furthermore incorporate a data logging & visualization pipeline using `MongoDB` for long-lived storage, `Grafana` (Infinity) for domain data visualization and `FastAPI` backend for log & BLE data retrieval from the MongoDB. `EMQX` is used as the MQTT broker with the community version `Docker` image, the setup for configurations neccessary for MQTT client connection(s) and MongoDB connector are automated in a init script. TinyGo Bluetooth library is used to incorporate `BLE` where a peripheral device can be registered and used in authentication to access the vault padlock, acting as a central BLE device. To protect the API routes, JWT tokens are used to authenitcate access. An additional init script is used to configure Grafana Infinity authentication method. Working default settings are found in `.env` files, (BLE peripheral service & characteristic requires manual input into /BLE/.env)

MQTT communications, is demonstrated through arbitrary data generation from `(VaultPadlock)`. Data is communicated to another MQTT app simulating a control device `(ControlComputer)`, it processes received data and detects a failed access attempts on the padlock and triggers a response to indefinitely lock. The Monitor application `(MonitorApp)` allows for selectively subscribing to topics to view communications and send message to any specificied topic, this is a basic CLI version of `MQTTX`. 

Defined topics in this project follow the structure as: `vault/padlock/{endpoint}`

**NOTE: This project has no pratical use as an effective vault lockpad system and does not interface with hardware.**

---

### System Components

#### 1. **MQTT & EMQX** 
The project has simulation of IoT device sending data using MQTT protocol using EMQX as the broker. EMQX dashboard can be accessed and has been pre-configured to establish client connections and connect the the MongoDB.
#### 2. **MongoDB** 
long-term storage and ease of use for development because it is non-relational database. MongoDB has a connector type avaliable for EMQX dashboard.
#### 3. **FastAPI** 
Python backend framework to enable integration of Grafana (Infinity) to retrieve logs from MongoDB (MongoDB datasource is limited to Grafana Enterprise version). Using JWT to protect API and only allow Grafana access to routes.
#### 4. **Grafana**
Dashboard & data visualization tool use to showcase business/domain data) which EMQX dashboard does not collect (e.g. cpu_temp)
#### 5. **BLE**
Bluetooth low-energy, used to register a device and provide it a token is used to verify the device is near to allow an access attempt.
#### 6. **Docker**
To enable easy & consistent deployments across various platforms.

---

### **Indefinite Lockout Mechanism:**

- When the Control Computer detects > 3 login attempts, it publishes a lockout message to the vault padlock.
- The padlock sets its state to `"INDEFINITE_LOCKED"` with error message: `"ACCESS FAILURE: TOO MANY UNLOCK ATTEMPTS DETECTED"`
- Access attempts are made interactively on the vault padlock program.

---

### **System Architecture** 

<img src="architecture.png" alt="screenshot" width="700">

---

### Data Flow (MQTT)

```
(Note: EMQX broker is transparent in diagram)

VaultPadlock                               ControlComputer
   |                                             |
   | --- publish status,metrics,events,ble ----> |  Process MQTT packets
   |                                             | 
   | <-----------  publish ble data  ----------- |  
   |                                             |
   | <--------  publish lockout signal  -------  |  (when access attempts > 3)
   |                                             |
   +-------- enters INDEFINITE_LOCKED state
```
---

### Deployment Steps
0. **Preliminary:**
   ```
   Ensure Docker engine is running
   Ensure python dependencies are installed: (execute `uv sync` in both MQTT Lockpad\backend, MQTT Lockpad\IoT)
   ```
1. **Docker compose deployment:**
   ```
   docker compose up
   (Deploys EMQX, Backend, MongoDB, Grafana & runs init scripts)
   ```
2. **LightBlue app setup**
   ```
   https://punchthrough.com/lightblue
   Install application and create a virtual device and follow below instructions:
   - Set name of virtual device: 'padlockAuth'
   - Create service & characteristic  and take note of ServiceUUID & CharacteristicUUID
   - Enable permissions: 'read', 'Write', 'Write without Response' for Characteristic
   - Finally, insert respective UUIDs into .env file in /BLE directory
   ```
3. **IoT devices (execute each in new terminal):**
   ```
   MQTT Lockpad\IoT
   uv run -m app.VaultPadlock (activate LightBlue virtual device too)
   uv run -m app.ControlComputer
   uv run -m app.MonitorApp (Optional)

   (Note: Once BLE device is registered, authentication would only be possible with this device unless manually removed from MongoDB. Program's flow will adjust to new registration or if BLE data exists accordingly)
   ```
4. **View EMQX dashboard, MongoDB, Grafana:**
   ```
   - default credentials for all logins (username: 'admin', password: 'password')
   
   - EMQX Dashboard: 'http://localhost:18083'
   - Grafana dashboard: 'http://localhost:3000'
   - MongoDB connection string: mongodb://admin:password@localhost:27017/VaultPadlock?authSource=admin
   ```
   (Note: Grafana's provisioning does not have a detailed dashboard but still showcases the ability to retrieve logs, creating and saving a dashboard will persist through the container's volume)
---

### Project Structure
```
MQTT Lockpad/
├── BLE/
│   ├── cmd/           # Main execution path
│   └── internal/      # BLE discovery, registration and detection
│   
├── IoT/               # Main MQTT simulation devices & EMQX broker init
│   ├── app/           # Main application modules (VaultPadlock, ControlComputer, MonitorApp)
│   ├── connection/    # MQTT broker connection configuration
│   ├── data/          # Data generators for padlock and control messages
│   ├── emqx/          # Provisioning configurations & init automation
│   ├── lock/          # Indefinite lock detection & enforcement logic
│   ├── schemas/       # Pydantic models for data validation
│   ├── services/      # MonitorApp, ControlComputer & VaultPadlock service classes
│   └── utils/         # Helper modules (console output, lockout detection, signal handling)
│
├── backend/           # FastAPI backend
|   ├── auth/          # Route authentication & creation for jwt
│   ├── connection/    # MongoDB Connection
│   └── vaultpadlock/  # Routes, schema & repository for vault padlock
│   └── ble/           # Route, schema & repository for ble data
│
└── grafana/           # Store provisioning config & JSON files
    ├── dashboards/    # Dashboard structure and settings
    └── provisioning/  # Config YAML files for datasources & dashboards
```
