## Overview

**MQTT** (Message Queuing Telemetry Transport) is a lightweight, publish–subscribe messaging protocol used for reliable communication between devices in distributed systems. It operates through a central broker that manages message exchange between clients, allowing devices to publish data to topics and subscribe to receive updates. This design enables efficient, real-time, and scalable communication, making MQTT widely used in IoT, automation, and remote monitoring applications.

**MQTT Vault Padlock** Is a project to demostrate MQTT communications and furthermore incorporate a data logging & visualization pipeline using `MongoDB` for long-lived storage, `Grafana` (Infinity) for enhanced visuals beyond EMQX dashboard and `FastAPI` backend for log retrieval from the MongoDB and then use in Grafana. `EMQX` is used as the MQTT broker as the community version `Docker` image, The setup for configurations neccessary for MQTT client connection(s) and MongoDB connector are automated in a init script using the default `.env` file.

MQTT communications, is demonstrated through arbitrary data generation from `(VaultPadlock)`. Data is communicated to another MQTT app simulating a control device `(ControlComputer)`, it processes received data and detects a brute force attempt on the padlock and triggers a response to indefinitely lock. The Monitor application `(MonitorApp)` allows for selectively subscribing to topics to view communications and send message to any specificied topic, this is a basic CLI version of `MQTTX`. 

Defined topics in this project follow the structure as: `vault/padlock/{endpoint}`

**NOTE: This project has no pratical use as an effective vault lockpad system and does not inteface with hardware.**

---

### System Components

#### 1. **VaultPadlock** (`app/VaultPadlock.py`)
A simulation of IoT device sending data using MQTT protocol

**Responsibilities:**
- Generates arbitrary data to send to control device.
- Detects lockout triggers and enters **INDEFINITE_LOCKED** state when too many failed login attempts are detected
- Displays sending and recieving MQTT messages

**Key Topics:**
- **Publishes to:** `status`, `metrics`, `event`
- **Subscribes to:** `vault/padlock/{device_id}`

#### 2. **ControlComputer** (`app/ControlComputer.py`)
The central control system that monitors padlock health and enforces security policies.

**Responsibilities:**
- Monitors access attempts by analysing event data
- When attempts exceed threshold (>3), publishes a lockout signal to trigger the indefinite lock mechanism
- Displays all received messages and sent commands

**Key Topics:**
- **Publishes to:** `control`, `device_id`
- **Subscribes to:** `status`, `metrics`, `event`

#### 3. **MonitorApp** (`app/MonitorApp.py`)
An interactive monitoring for observing system communication.

**Responsibilities:**
- Allows manual monitoring of any MQTT topic in real-time
- Supports both send and receive modes

---

### **Indefinite Lockout Mechanism:**

- When the Control Computer detects > 3 login attempts, it publishes a lockout message to the vault padlock.
- The padlock sets its state to `"INDEFINITE_LOCKED"` with error message: `"ACCESS FAILURE: TOO MANY UNLOCK ATTEMPTS DETECTED"`
- The system sleeps for 30 seconds to maintain the locked state, then returns and repeats.
- (This is entirely for demonstration purposes and has no practical security implications)

---

### Data Flow

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
   Ensure Docker engine is running and python dependencies & requirements are installed (requirements.txt)
   ```
1. **Docker compose deployment:**
   ```
   docker compose up 
   ```
2. **Init automation (Ensure EMQX container is healthy):**
   ```
   python -m emqx.init

   (Note: This script does not need to be run again unless rebuilding containers or you have deleted EMQX container volumes)
   ```

3. **IoT devices (execute each in new terminal):**
   ```
   python -m app.VaultPadlock
   python -m app.ControlComputer
   python -m app.MonitorApp (Optional)
   ```
4. **View EMQX dashboard & MongoDB:**
   ```
   - search url: 'http://localhost:18083'
   - Login into EMQX dashboard with default credentials (username: 'admin', password: 'password')
   - MongoDB connection string: mongodb://admin:password@localhost:27017/VaultPadlock?authSource=admin
   ```
---

### Project Structure

- `app/` — Main application modules (VaultPadlock, ControlComputer, MonitorApp)
- `connections/` — MQTT broker connection configuration
- `data/` — data generators for padlock and control messages
- `emqx`/  — Provisioning configurations & init automation
- `lock`/  — Indefinite lock detection & enforcement logic
- `schemas/` — Pydantic models for data validation 
- `services/` — Monitor app logic for interface interaction 
- `utils/` — Helper modules (console output, lockout detection, signal handling)
