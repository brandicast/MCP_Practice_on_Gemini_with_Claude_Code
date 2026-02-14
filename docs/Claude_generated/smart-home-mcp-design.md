# Smart Home MCP Tool Design Document

**Project**: gemini_api_trail - project_2
**Date**: 2025-02-10
**Purpose**: Add MQTT-based IoT monitoring and Gemini function calling for smart home status queries

---

## Table of Contents
1. [Current Architecture Overview](#current-architecture-overview)
2. [Proposed MCP Tool Design](#proposed-mcp-tool-design)
3. [Files to be Modified/Created](#files-to-be-modifiedcreated)
4. [Implementation Flow](#implementation-flow)
5. [Open Questions / TODOs](#open-questions--todos)

---

## Current Architecture Overview

### Project Structure
```
project_2/
├── server.py              # Flask web server
├── gemini/
│   └── agent.py          # Gemini API integration & session management
├── util/
│   └── typing.py         # Session class definition
├── requirements.txt
└── Dockerfile
```

### server.py Flow
1. **Startup**: Calls `AI.loadChatSession()` to restore saved sessions from `history/` directory
2. **Root endpoint** (`/`): Returns "Hello" for health checks
3. **Chat endpoint** (`/chat/id/<user>`):
   - Accepts user ID in URL path
   - Accepts question via `ask` query parameter
   - Delegates to `AI.ask(user, content)`
   - Returns stripped text response
4. **History endpoint** (`/chat/history/<user>`):
   - Returns HTML-wrapped chat history for a user

### gemini/agent.py Flow
1. **Module initialization**:
   - Configures Gemini API with `API_KEY` from environment
   - Loads system instruction from `./resources/system_instruction.txt`
   - Initializes global state: `model`, `sessions_cache`, `last_dump_time`
   - Starts background thread for history persistence

2. **Session restoration** (`loadChatSession()`):
   - Scans `history/` directory for pickle files
   - Deserializes conversation histories
   - Recreates `Session` objects with chat instances
   - Stores in `sessions_cache` by user ID

3. **Chat handling** (`ask(id, content)`):
   - Creates new session if user ID not in cache
   - Sends message via `session.chat.send_message(content)`
   - Catches `StopCandidateException` for safety blocks
   - Updates session timestamp
   - Returns answer text or Chinese error message

4. **Model initialization** (`getModel()`):
   - Singleton pattern - creates model once
   - Uses `gemini-2.5-flash`
   - Applies system instruction and custom safety settings

5. **Background persistence**:
   - Thread runs `historyPersistent()` every 60 seconds
   - Compares session timestamps against `last_dump_time`
   - Serializes modified chat histories to pickle files

### Current Technology Stack
- **Python 3.11+**
- **Flask 3.0.3**: Web server
- **google-generativeai 0.7.2**: Gemini API client
- **protobuf 4.25.4**: Protocol buffers

---

## Proposed MCP Tool Design

### Overview
Add two major components:
1. **MQTT Client**: Subscribe to IoT device status updates and maintain in-memory state
2. **MCP Tool**: Gemini function calling tool to query IoT device status

### Component 1: MQTT Client

#### Purpose
Background subscriber that maintains real-time IoT device status in memory, accessible to other modules.

#### Global State
```python
iot_devices_status = {}      # Latest IoT status JSON
iot_status_lock = threading.Lock()  # Thread-safe access
mqtt_client = None           # MQTT client instance
GRACEFULLY_STOP = False      # Shutdown flag
```

#### Configuration (Environment Variables)
- `topic_for_iot`: MQTT topic to subscribe to (required)
- `MQTT_BROKER_HOST`: MQTT broker address (required)
- `MQTT_BROKER_PORT`: MQTT broker port (default: 1883)
- `MQTT_USERNAME`: Optional authentication username
- `MQTT_PASSWORD`: Optional authentication password

#### Expected IoT Status JSON Structure
```json
{
  "timestamp": "2025-02-10T10:30:00Z",
  "devices": [
    {
      "device_id": "light_001",
      "device_type": "light",
      "room": "living_room",
      "status": "on",
      "brightness": 80
    },
    {
      "device_id": "temp_sensor_001",
      "device_type": "sensor",
      "room": "bedroom",
      "status": "active",
      "temperature": 22.5,
      "humidity": 45
    }
  ]
}
```

#### MQTT Client Functions
- `on_connect(client, userdata, flags, rc)`: Handle connection events
- `on_message(client, userdata, msg)`: Parse incoming JSON and update `iot_devices_status`
- `mqtt_subscriber_job()`: Main loop - connect to broker, subscribe, maintain connection
- `get_iot_status(device_id=None, device_type=None, room=None)`: Thread-safe accessor with optional filtering

#### Lifecycle
- Starts automatically when `iot.mqtt_client` module is imported
- Runs in background thread (similar to `historyPersistentJob`)
- Continues until `GRACEFULLY_STOP = True`

### Component 2: MCP Tool - `get_smart_home_status`

#### Tool Interface

**Function Declaration** (Gemini Function Calling):
```python
{
  "name": "get_smart_home_status",
  "description": "Retrieves the current status of IoT smart home devices collected from MQTT",
  "parameters": {
    "type": "object",
    "properties": {
      "device_id": {
        "type": "string",
        "description": "Filter by specific device ID"
      },
      "device_type": {
        "type": "string",
        "description": "Filter by device type (e.g., 'light', 'sensor', 'thermostat')"
      },
      "room": {
        "type": "string",
        "description": "Filter by room location (e.g., 'living_room', 'bedroom')"
      }
    }
  }
}
```

#### Registration Point
**Location**: `gemini/agent.py` → `getModel()` function (lines 82-92)

**Changes**:
- Add function declaration using `genai.protos.FunctionDeclaration`
- Create `genai.protos.Tool` containing the function
- Pass `tools=[...]` parameter to `GenerativeModel()` constructor

#### Execution Point
**Location**: `gemini/agent.py` → `ask()` function (lines 51-79)

**Flow**:
1. After `session.chat.send_message(content)` returns response
2. Check if response contains `function_call` in parts
3. If yes:
   - Extract function name and arguments
   - Call `execute_function_call()` helper
   - Execute `get_iot_status(**arguments)` from mqtt_client module
   - Send function result back via `session.chat.send_message()`
   - Get final natural language response from Gemini
4. If no: return text response as normal

---

## Files to be Modified/Created

### New Files

#### 1. `project_2/iot/__init__.py`
- **Purpose**: Make `iot` a Python package
- **Content**: Empty file

#### 2. `project_2/iot/mqtt_client.py`
- **Purpose**: MQTT client implementation and IoT status management
- **Contents**:
  - Global variables: `iot_devices_status`, `iot_status_lock`, `mqtt_client`, `GRACEFULLY_STOP`
  - Callback functions: `on_connect()`, `on_message()`
  - Main function: `mqtt_subscriber_job()`
  - Public accessor: `get_iot_status(device_id=None, device_type=None, room=None)`
  - Module-level thread initialization
- **Dependencies**: `paho-mqtt`, `threading`, `json`, `os`, `logging`

#### 3. `project_2/.env.example`
- **Purpose**: Document required environment variables
- **Contents**:
  ```
  API_KEY=your_gemini_api_key
  topic_for_iot=home/devices/status
  MQTT_BROKER_HOST=mqtt.example.com
  MQTT_BROKER_PORT=1883
  MQTT_USERNAME=optional_username
  MQTT_PASSWORD=optional_password
  ```

### Modified Files

#### 4. `project_2/gemini/agent.py`

**Import additions** (after line 7):
```python
from iot.mqtt_client import get_iot_status
```

**Function `getModel()` modifications** (lines 82-92):
- Define function declaration for `get_smart_home_status`
- Add `tools=[...]` parameter to `genai.GenerativeModel()` constructor

**Function `ask()` modifications** (lines 51-79):
- After line 70: Add function call detection and handling loop
- Check `response.parts` for `function_call` attribute
- If detected: execute function, send result back, get final response
- Update answer extraction to handle function call flow

**New helper function** `execute_function_call()`:
- Extract function name and arguments from `function_call` object
- Route to appropriate function (currently only `get_smart_home_status`)
- Call `get_iot_status(**arguments)`
- Return filtered JSON result

#### 5. `project_2/requirements.txt`

**Add**:
```
paho-mqtt==1.6.1
```

#### 6. `project_2/Dockerfile`

**Add environment variables** (after line 16):
```dockerfile
ENV topic_for_iot=home/devices/status
ENV MQTT_BROKER_HOST=localhost
ENV MQTT_BROKER_PORT=1883
```

**Ensure history directory** (line 14 already creates it):
```dockerfile
RUN mkdir -p history
```

---

## Implementation Flow

### Startup Sequence
```
1. server.py starts
   ↓
2. Imports gemini.agent
   ↓
3. agent.py imports iot.mqtt_client
   ↓
4. mqtt_client.py module initialization:
   - Creates global variables
   - Starts MQTT background thread
   ↓
5. MQTT thread:
   - Connects to broker
   - Subscribes to topic_for_iot
   - Begins listening for messages
   ↓
6. server.py calls AI.loadChatSession()
   ↓
7. Flask app.run(host='0.0.0.0')
```

### Runtime: MQTT Message Handling
```
MQTT message received on topic_for_iot
   ↓
on_message() callback triggered
   ↓
Parse JSON payload
   ↓
Acquire iot_status_lock
   ↓
Update iot_devices_status global dict
   ↓
Release lock
   ↓
Log update
```

### Runtime: User Query with Function Calling
```
User request: "What's the temperature in the bedroom?"
   ↓
GET /chat/id/user123?ask=What's the temperature in the bedroom?
   ↓
server.py → AI.ask('user123', 'What's the temperature in the bedroom?')
   ↓
agent.py → session.chat.send_message(content)
   ↓
Gemini API analyzes request
   ↓
Gemini decides to call function: get_smart_home_status(room="bedroom", device_type="sensor")
   ↓
Response contains function_call part
   ↓
agent.py detects function_call
   ↓
execute_function_call() → get_iot_status(room="bedroom", device_type="sensor")
   ↓
Acquire iot_status_lock
   ↓
Filter iot_devices_status by room and device_type
   ↓
Release lock
   ↓
Return filtered JSON
   ↓
agent.py sends function result back to Gemini
   ↓
Gemini generates natural language response:
"The bedroom temperature is currently 22.5°C with 45% humidity."
   ↓
Return response to user
```

---

## Open Questions / TODOs

### Design Decisions

1. **MQTT Message Format**
   - [ ] Confirm exact JSON structure from IoT devices
   - [ ] Handle partial updates vs. full device list
   - [ ] Define behavior for invalid/malformed JSON messages

2. **Error Handling**
   - [ ] What happens if MQTT broker is unreachable at startup?
   - [ ] Should we retry connection? How often?
   - [ ] Should we return stale data or error if MQTT disconnects?
   - [ ] How to handle empty `iot_devices_status` (no data received yet)?

3. **Function Call Flow**
   - [ ] Should we limit function call recursion depth?
   - [ ] How to handle if Gemini requests multiple sequential function calls?
   - [ ] Should function execution timeout?

4. **Data Freshness**
   - [ ] Add timestamp to `iot_devices_status` to track data age?
   - [ ] Return age of data in function response?
   - [ ] Define "stale data" threshold (e.g., >5 minutes old)?

5. **Security**
   - [ ] Should MQTT credentials be encrypted at rest?
   - [ ] Add TLS/SSL support for MQTT connection?
   - [ ] Validate MQTT message source/authenticity?

### Implementation TODOs

#### Phase 1: MQTT Client
- [ ] Create `iot/` package structure
- [ ] Implement `mqtt_client.py` with basic connection
- [ ] Test MQTT subscription and message reception
- [ ] Implement thread-safe status updates
- [ ] Add logging for connection events and errors
- [ ] Test reconnection logic on broker failure

#### Phase 2: Function Declaration
- [ ] Define function schema in `agent.py`
- [ ] Register tool with `GenerativeModel`
- [ ] Test that Gemini recognizes the function

#### Phase 3: Function Execution
- [ ] Implement `execute_function_call()` helper
- [ ] Add function call detection in `ask()`
- [ ] Implement function result sending back to Gemini
- [ ] Handle function call errors gracefully

#### Phase 4: Integration Testing
- [ ] Test end-to-end flow with mock MQTT broker
- [ ] Test with real IoT devices
- [ ] Test error cases:
  - No data available
  - MQTT disconnected
  - Invalid function arguments
  - Gemini safety blocks
- [ ] Performance test with multiple concurrent users

#### Phase 5: Documentation
- [ ] Update CLAUDE.md with MQTT setup instructions
- [ ] Document IoT JSON schema requirements
- [ ] Add example queries and expected responses
- [ ] Update Dockerfile with MQTT environment variables

### Missing Requirements

1. **System Instruction Update**
   - [ ] Does `resources/system_instruction.txt` need updates to guide Gemini on when to use the function?
   - [ ] Should we add examples of smart home queries to the system instruction?

2. **Persistent State**
   - [ ] Should `iot_devices_status` be persisted to disk?
   - [ ] If yes, how to handle stale persisted data on restart?

3. **Multi-tenant Considerations**
   - [ ] Currently single global `iot_devices_status` - is this per-user or shared?
   - [ ] If per-user, need to map user ID to their device status
   - [ ] Security: prevent users from querying other users' devices

4. **Monitoring & Observability**
   - [ ] Add metrics for MQTT message rate
   - [ ] Add metrics for function call success/failure
   - [ ] Health check endpoint that includes MQTT connection status?

5. **Graceful Shutdown**
   - [ ] Implement signal handling for `GRACEFULLY_STOP` flag
   - [ ] Ensure MQTT client disconnects cleanly
   - [ ] Wait for background threads to complete on shutdown

### Testing Strategy

- [ ] Unit tests for `get_iot_status()` filtering logic
- [ ] Unit tests for MQTT message parsing
- [ ] Integration tests for function calling flow
- [ ] Mock MQTT broker for CI/CD testing
- [ ] Load testing with multiple simultaneous chat sessions

---

## References

- **Gemini Function Calling**: https://ai.google.dev/gemini-api/docs/function-calling
- **Paho MQTT Python**: https://www.eclipse.org/paho/index.php?page=clients/python/index.php
- **Google AI Python SDK**: https://github.com/google/generative-ai-python

---

**Document Status**: Draft
**Next Review**: After Phase 1 implementation
**Owner**: Development Team
