## Overview

**MQTT Vault Lockpad** is a distributed IoT security system that monitors and controls a vault padlock using MQTT messaging. The system consists of three main applications that communicate over MQTT topics to manage authentication, access control, and security lockout mechanisms.

### System Components

#### 1. **VaultPadlock** (`app/VaultPadlock.py`)
The vault padlock device simulator that runs on the physical/mock padlock system.

**Responsibilities:**
- Generates mock padlock **status data** (locked/unlocked state, errors)
- Generates mock padlock **metrics** (CPU, login attempts, network stats)
- Publishes status and metrics to `TOPICS.status` and `TOPICS.metrics`
- Subscribes to control commands from the Control Computer
- Detects lockout triggers and enters **INDEFINITE_LOCKED** state when too many failed login attempts are detected
- Displays lockout alerts in terminal without sending additional MQTT messages

**Key Topics:**
- **Publishes to:** `status`, `metrics`
- **Subscribes to:** `control`, `lockout`

---

#### 2. **ControlComputer** (`app/ControlComputer.py`)
The central control system that monitors padlock health and enforces security policies.

**Responsibilities:**
- Publishes keepalive/control commands to the padlock
- Subscribes to padlock status and metrics
- Monitors `login_attempts` in metrics data
- When login attempts exceed threshold (>5), publishes a lockout signal to trigger the indefinite lock mechanism
- Logs all received messages and sent commands

**Key Topics:**
- **Publishes to:** `control`, `lockout`
- **Subscribes to:** `status`, `metrics`

---

#### 3. **MonitorApp** (`app/MonitorApp.py`)
An interactive monitoring and debugging tool for observing system communication.

**Responsibilities:**
- Allows manual monitoring of any MQTT topic in real-time
- Supports both send and receive modes for topic inspection

---

### Security Features

**Indefinite Lockout Mechanism:**
- When the Control Computer detects > 5 login attempts, it publishes a lockout signal to `TOPICS.lockout`
- The VaultPadlock receives this signal and immediately enters an indefinite locked state
- The padlock sets its state to `"INDEFINITE_LOCKED"` with error message: `"ACCESS FAILURE: TOO MANY UNLOCK ATTEMPTS DETECTED"`
- The system sleeps for 30 seconds to maintain the locked state, then returns to normal operation
- (This is entirely for system demonstration purposes and has no real pratical security implications)

---

### Data Flow

```
VaultPadlock                    ControlComputer
   |                                 |
   |-- publish status/metrics ------>|
   |                                 |
   |<-- publish control commands ----|
   |                                 |
   |<-- publish lockout signal ------|  (when attempts > 5)
   |
   +-- enters INDEFINITE_LOCKED state
   +-- Will return to LOCKED and repeat
```

---

### Technologies

- **MQTT Broker:** Paho MQTT client library for Python
- **Data Validation:** Pydantic for schema validation
- **Threading:** Multi-threaded design for concurrent publish/subscribe operations
- **Abstract Base Classes:** The system uses an abstract base class (MQTTApp) to define the core MQTT client behavior, enforcing implementation of essential methods - publish() and subscribe().

---

### Running the Application

Ensure you have an MQTT broker running (e.g., EMQX ) or cloud connection, then start:

1. **VaultPadlock (in terminal 1):**
   ```
   python -m app.VaultPadlock
   ```

2. **ControlComputer (in terminal 2):**
   ```
   python -m app.ControlComputer
   ```

3. **MonitorApp (optional, in terminal 3):**
   ```
   python -m app.MonitorApp
   ```

---

### Project Structure

- `app/` — Main application modules (VaultPadlock, ControlComputer, MonitorApp)
- `mock/` — Mock data generators for padlock and control messages
- `schemas/` — Pydantic models for data validation (Topics, VaultPadlockMetrics, ControlComputerLock)
- `connections/` — MQTT broker connection configuration
- `utils/` — Helper modules (console output, lockout detection, signal handling)
- `services/` — Business logic services (MonitorAppService) 