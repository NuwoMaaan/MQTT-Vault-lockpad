## Overview

**MQTT** (Message Queuing Telemetry Transport) is a lightweight, publish–subscribe messaging protocol used for reliable communication between devices in distributed systems. It operates through a central broker that manages message exchange between clients, allowing devices to publish data to topics and subscribe to receive updates. This design enables efficient, real-time, and scalable communication, making MQTT widely used in IoT, automation, and remote monitoring applications.

**MQTT Vault Padlock** Is a project to demostrate MQTT communications and furthermore incorporate a data logging & visualization pipeline using `MongoDB` for long-lived storage, `Grafana` (Infinity) for domain data visualization and `FastAPI` backend for log & BLE data retrieval from the MongoDB. `EMQX` is used as the MQTT broker with the community version `Docker` image, the setup for configurations neccessary for MQTT client connection(s) and MongoDB connector is provisioned declaratively. TinyGo Bluetooth library is used to incorporate `BLE` where a peripheral device can be registered and used in authentication to access the vault padlock, acting as a central BLE device. To protect the API routes, JWT tokens are used to authenitcate access. A background backend init script is used to configure Grafana Infinity authentication method. Working default settings are found in `.env` files, (BLE peripheral service & characteristic requires manual input into /BLE/.env)

MQTT communications, is demonstrated through arbitrary data generation from `(VaultPadlock)`. Data is communicated to another MQTT app simulating a control device `(ControlComputer)`, it processes received data and detects a failed access attempts on the padlock and triggers a response to indefinitely lock. The Monitor application `(MonitorApp)` allows for selectively subscribing to topics to view communications and send message to any specificied topic, this is a basic CLI version of `MQTTX`. 

Defined topics in this project follow the structure as: `vault/padlock/{endpoint}`

**NOTE: This project has no pratical use as an effective vault lockpad system and does not interface with hardware.**

---
### **System Architecture** 

<img src="architecture.png" alt="screenshot" width="700">

---
### System Components

#### 1. **MQTT & EMQX** 
- IoT devices connect and communicate using MQTT protocol via the EMQX broker   
- EMQX broker is pre-configured to establish client connections, authentication method, MongoDB connector and, rules & actions      
- All published metrics, status, and event data are automatically captured by EMQX broker rules and forwarded to MongoDB for persistent storage and data retrieval.    

#### 2. **IoT Applications** 
##### **Vault Padlock**
- The Vault Padlock is an MQTT-connected IoT device that manages secure access to physical vaults using a 2FA authentication system combining BLE (Bluetooth Low Energy) device verification and CLI-based passcode authentication  
- A token is inserted into the peripheral device, access requires both the valid BLE device to be in proximity AND the correct passcode      
- Publishes system metrics and lock status every non-abitrary amount of time but on occurence publishes events & BLE data requests  
- Uses a Golang BLE subprocess that handles Bluetooth operations including device discovery, registration, and presence detection  
- interprocess communication is achieved by stdin & stdout to relay BLE data to each process 
- BLE device data is stored in MongoDB, a retrieval process executes to get existing BLE device data and relayed to Golang subprocess
##### **Control Computer**
- The Control Computer serves as the central monitoring and management hub for the Vault Padlock ecosystem. It monitors real-time device data, enforces security policies, manages authentication with the backend API, and coordinates BLE device data retrieval between the backend and vault padlock.
- Provides authenticated API access to fetch and store BLE credentials securely via the backend and bridges data to and from vault padlock
- Maintains continuous authenticated communication with the backend API using JWT, an automatic token refresh service loop proactively refreshes tokens 5 minutes before expiry
##### **Monitoring App**
- An interactive CLI utility for real-time MQTT topic monitoring and message publishing
- Capable of subscribing to multiple system topics simultaneously, publish test messages, and listen for incoming messages from vault padlock and the control computer

#### 3. **MongoDB** 
- long-term storage and ease of use for development because it is a non-relational database. MongoDB has a connector type avaliable for EMQX dashboard, enabling database insertion directly from EMQX broker
- Stores status, metric, event and BLE device data
  
#### 4. **FastAPI Backend** 
- Python backend framework to enable integration of Grafana (Infinity) to retrieve logs from MongoDB (MongoDB datasource is limited to Grafana Enterprise version), enable integration with IoT control computer application providing BLE device data retrieval bridge path
- Route endpoints are protected with JWT authentication, tokens contain specific permissions only allowing access to particular routes
- Configures Grafana Infinity datasource with a background service that inserts & maintains valid JWT for Grafana enabling secure access as a long-lived token service

#### 5. **Grafana**
- Dashboard & data visualization tool use to showcase business/domain data which EMQX dashboard does not collect (e.g. cpu_temp, access_attempts)
- YAML configuration files are loaded into application container with docker volumes for provisioning of dashboard & settings
- Grafana Infinity datasource is used to enable data retrieval through API access and complete securely using bearer token authentication method
  
#### 6. **BLE**
- BLE (Bluetooth Low Energy) is used to register a device and provide it a token, enabling a 2FA (two-factor authentication) mechanism through proximity-based verification
- Follows the Generic Attribute Profile (GATT) model, where devices expose structured data via Services and Characteristics identified by UUIDs
- A virtual or physical BLE peripheral device (e.g. padlockAuth) advertises its presence, while the Vault Padlock acts as a central device that scans, connects, and interacts with it
- Registered BLE device metadata (name, UUIDs, tokens) is persisted in MongoDB and retrieved at runtime to validate proximity-based authentication attempts
- Authentication data (token) is exchanged via a predefined Characteristic, with permissions read, write, and write without response controlling access
- Presence detection is achieved through periodic scanning; successful identification of a registered device satisfies the second authentication factor

#### 7. **Docker**
- Docker enables easy & consistent/idempotent deployments across different platforms and allows fast development testing
- Docker container services in project: emqx, emqx-init, backend, mongo, grafana
- Docker-compose is used to orchestrate fast and easy deployment
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
### **Indefinite Lockout Mechanism:**

- When the Control Computer detects > 3 login attempts, it publishes a lockout message to the vault padlock.
- The padlock sets its state to `"INDEFINITE_LOCKED"` with error message: `"ACCESS FAILURE: TOO MANY UNLOCK ATTEMPTS DETECTED"`
- Access attempts are made interactively on the vault padlock program.
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
   (Deploys EMQX, Backend, MongoDB, Grafana)
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
│   ├── cmd/               # Main execution path
│   └── internal/          # BLE discovery, registration and detection
│   
├── IoT/                   # Main MQTT simulation devices & EMQX broker init
│   ├── app/               # Main application modules (VaultPadlock, ControlComputer, MonitorApp)
│   ├── connection/        # MQTT broker connection configuration
│   ├── data/              # Data generators for padlock and control messages
│   ├── lock/              # Indefinite lock detection & enforcement logic
│   ├── schemas/           # Pydantic models for data validation
│   ├── services/          # MonitorApp, ControlComputer & VaultPadlock service classes
│   └── utils/             # Helper modules (console output, lockout detection, signal handling)
│
├── emqx/              
│   └── provisioning/      # Provisioning configurations for broker
|       ├── declarative/   # configuration via bind volume mount 
|       └── imperative/    # configuration via EMQX API calls (deprecated)
|
├── backend/               # FastAPI backend
|   ├── auth/              # Route authentication & creation for jwt
│   ├── connection/        # MongoDB Connection
│   ├── vaultpadlock/      # Routes, schema & repository for vault padlock
│   └── ble/               # Route, schema & repository for ble data
│
└── grafana/               # Store provisioning config & JSON files
    ├── dashboards/        # Dashboard structure and settings
    └── provisioning/      # Config YAML files for datasources & dashboards
```
