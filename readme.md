## Overview

**MQTT** (Message Queuing Telemetry Transport) is a lightweight, publish–subscribe messaging protocol used for reliable communication between devices in distributed systems. It operates through a central broker that manages message exchange between clients, allowing devices to publish data to topics and subscribe to receive updates. This design enables efficient, real-time, and scalable communication, making MQTT widely used in IoT, automation, and remote monitoring applications.

**MQTT Vault Padlock** Is a project to demostrate MQTT communications and furthermore incorporate a data logging & visualization pipeline using `MongoDB` for long-lived storage, `Grafana` (Infinity) for domain data visualization and `FastAPI` backend for log retrieval from the MongoDB and then use in Grafana. `EMQX` is used as the MQTT broker as the community version `Docker` image, The setup for configurations neccessary for MQTT client connection(s) and MongoDB connector are automated in a init script. To protect the API routes, JWT tokens are used to authenitcate access. An additional init script is used to configure Grafana Infinity authentication method. Working default settings are found in `.env` files.

MQTT communications, is demonstrated through arbitrary data generation from `(VaultPadlock)`. Data is communicated to another MQTT app simulating a control device `(ControlComputer)`, it processes received data and detects a brute force attempt on the padlock and triggers a response to indefinitely lock. The Monitor application `(MonitorApp)` allows for selectively subscribing to topics to view communications and send message to any specificied topic, this is a basic CLI version of `MQTTX`. 

Defined topics in this project follow the structure as: `vault/padlock/{endpoint}`

**NOTE: This project has no pratical use as an effective vault lockpad system and does not inteface with hardware.**

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
#### 5. **Docker**
To enable easy & consistent deployments across various platforms.

---

### **Indefinite Lockout Mechanism:**

- When the Control Computer detects > 3 login attempts, it publishes a lockout message to the vault padlock.
- The padlock sets its state to `"INDEFINITE_LOCKED"` with error message: `"ACCESS FAILURE: TOO MANY UNLOCK ATTEMPTS DETECTED"`
- The system sleeps for 30 seconds to maintain the locked state, then returns and repeats.
- (This is entirely for demonstration purposes and has no practical security implications)

---

### Data Flow (MQTT)

```
VaultPadlock                       ControlComputer
   |                                        |
   | --- publish status,metrics,events ---> |
   |                                        |
   | <---  publish control commands ------  |
   |                                        |
   | <---   publish lockout signal  ------  |  (when attempts > 3)
   |                                        |
   +-- enters INDEFINITE_LOCKED state
   +-- Will return to LOCKED and repeat
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
   docker compose up (Deploys EMQX, Backend, MongoDB, Grafana)
   ```
2. **Init automation (Ensure EMQX & Grafana containers are healthy):**
   ```
   MQTT Lockpad\IoT
   uv run -m emqx.init

   MQTT Lockpad\Backend
   uv run -m auth.init
   
   (Note: These script does not need to be run again unless rebuilding containers or you have deleted EMQX & Grafana container volumes)
   ```

3. **IoT devices (execute each in new terminal):**
   ```
   MQTT Lockpad\IoT
   uv run -m app.VaultPadlock
   uv run -m app.ControlComputer
   uv run -m app.MonitorApp (Optional)
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
├── IoT/               # Main MQTT simulation devices & EMQX broker init
│   ├── app/           # Main application modules (VaultPadlock, ControlComputer, MonitorApp)
│   ├── connection/    # MQTT broker connection configuration
│   ├── data/          # Data generators for padlock and control messages
│   ├── emqx/          # Provisioning configurations & init automation
│   ├── lock/          # Indefinite lock detection & enforcement logic
│   ├── schemas/       # Pydantic models for data validation
│   ├── services/      # Monitor app logic for interface interaction
│   └── utils/         # Helper modules (console output, lockout detection, signal handling)
│
├── backend/           # FastAPI backend
|   ├── auth/          # Route authentication with JWT
│   ├── connection/    # MongoDB Connection
│   └── vaultpadlock/  # Routes, schema & repository for vault padlock
│
└── grafana/           # Store provisioning config & JSON files
    ├── dashboards/    # Dashboard structure and settings
    └── provisioning/  # Config YAML files for datasources & dashboards
```
