# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a learning repository for experimenting with Google's Gemini API. It contains:
- **project_0**: Node.js examples using `@google/generative-ai`
- **project_1**: Python CLI examples (single prompt, chat, chat with instructions)
- **project_2**: Legacy Flask web service examples
- **src/**: Main production application - Flask web service with smart home IoT integration, Gemini function calling, and multi-user session management

## Environment Setup

### Basic Setup
All projects require the `API_KEY` environment variable set with a valid Google Gemini API key:
```bash
export API_KEY="your-gemini-api-key"
```

### Main Application (src/) Additional Requirements
The main application also requires MQTT configuration for IoT device monitoring:
```bash
export API_KEY="your-gemini-api-key"
export MQTT_BROKER_HOST="your-mqtt-broker-host"
export MQTT_BROKER_PORT="1883"
export MQTT_USERNAME="your-username"  # Optional
export MQTT_PASSWORD="your-password"  # Optional
export topic_for_iot="brandon/iot/zwave/philio/event/#"
```

**Using .env file:**
```bash
cp .env.example .env
# Edit .env with your actual credentials
```

## Running the Projects

### Project 0 (Node.js)
```bash
cd project_0
npm install
node test.js
# or
node bread.js
```

### Project 1 (Python CLI)
```bash
cd project_1
# Install google-generativeai if needed: pip install google-generativeai

# Simple single-turn interaction
python single.py

# Multi-turn chat with history
python chat.py

# Chat with system instruction and custom safety settings
python chat_with_instruction.py
```

All scripts accept user input until "EXIT" is entered.

### Main Application (src/) - Smart Home IoT Service

**Local Development:**
```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables (or use .env file)
export API_KEY="your-gemini-api-key"
export MQTT_BROKER_HOST="your-mqtt-broker"
export MQTT_BROKER_PORT="1883"
export topic_for_iot="brandon/iot/zwave/philio/event/#"

# Run the server
cd src
python server.py
```

**Docker Deployment:**
```bash
# Build the image
docker build -t gemini-smart-home .

# Run with environment variables
docker run -p 5000:5000 \
  -e API_KEY="your-api-key" \
  -e MQTT_BROKER_HOST="your-broker" \
  -e MQTT_BROKER_PORT="1883" \
  -e topic_for_iot="brandon/iot/zwave/philio/event/#" \
  -v $(pwd)/src/history:/code/src/history \
  gemini-smart-home
```

**API Endpoints:**
- `GET /chat/id/<user>?ask=<question>` - Ask a question as a specific user
- `GET /chat/history/<user>` - View chat history for a user

**Example Queries:**
```bash
# Ask about current time
curl "http://localhost:5000/chat/id/test?ask=現在幾點？"

# Ask about smart home temperature
curl "http://localhost:5000/chat/id/test?ask=五樓現在幾度？"

# Ask about door status
curl "http://localhost:5000/chat/id/test?ask=大門有關嗎？"
```

### Project 2 (Flask Web Service - Legacy)
```bash
cd project_2
pip install -r requirements.txt

# IMPORTANT: Create the resources directory and system_instruction.txt first
mkdir -p resources
echo "Your system instruction here" > resources/system_instruction.txt

python server.py
```

## Architecture

### Main Application Architecture (src/)

This is a production-ready Flask web service with smart home IoT integration and Gemini function calling capabilities.

**Project Structure:**
```
src/
├── gemini/
│   └── agent.py          # Gemini AI integration with function calling
├── iot/
│   ├── __init__.py       # IoT package exports
│   └── mqtt_client.py    # MQTT client for Philio Z-Wave devices
├── resources/
│   └── system_instruction.txt  # System instructions for Gemini
├── history/              # Persistent chat session storage
├── util/
│   └── typing.py         # Type definitions
└── server.py             # Flask web server
```

**Session Management** (`src/gemini/agent.py`):
- Maintains a global `sessions_cache` dict mapping user IDs to `Session` objects
- Each `Session` contains a Gemini chat instance and timestamp
- Sessions persist across requests for the same user ID

**History Persistence**:
- Background thread runs `historyPersistentJob()` every 60 seconds
- Saves conversation histories to `history/<user_id>` files using pickle
- On server startup, `loadChatSession()` restores sessions from history directory

**IoT/MQTT Integration** (`src/iot/mqtt_client.py`):
- Background MQTT subscriber thread monitors Philio Z-Wave device events
- Thread-safe in-memory device status cache (`iot_devices_status{}`)
- Automatic conversions:
  - Product codes (decimal → hex → device names)
  - Temperature (Fahrenheit → Celsius)
  - Timestamps (Unix → local time format)
- Supports 62 function types and 80+ event codes
- Query function with 4 filter parameters: device_name, user_name, device_type, event_type

**Gemini Function Calling** (`src/gemini/agent.py`):
- **get_smart_home_status**: Query IoT device status (temperature, doors, motion, power)
- **get_current_time**: Get current date/time with timezone support
- Automatic function detection and execution
- Natural language response synthesis

**Model Configuration**:
- Uses `gemini-2.5-flash` model
- System instruction loaded from `resources/system_instruction.txt`
- Function calling tools enabled
- Custom safety settings to allow most content (except high sexual/explicit)

**Error Handling**:
- Catches `StopCandidateException` when safety filters block responses
- Graceful MQTT connection failures (server continues without IoT data)
- Function execution errors returned to model for context-aware responses
- Returns Chinese error messages for safety blocks and general exceptions

**Data Flow:**
```
MQTT Broker (Philio Gateway)
    ↓ (IoT events)
mqtt_client.on_message()
    ↓ (parse, convert, store)
iot_devices_status{} (in-memory cache)
    ↓ (user query via Flask)
Gemini Function Call: get_smart_home_status()
    ↓ (filtered results)
Gemini Natural Language Response
    ↓
User: "五樓現在 21.7 度喔～"
```

## Important Notes

- **Model versions**: The codebase uses `gemini-2.5-flash` (1.5 is deprecated)
- **Python version**: Requires Python 3.10+ (tested with 3.10 and 3.11)
- **Required directories**:
  - `src/resources/` with `system_instruction.txt` (created automatically)
  - `src/history/` for session persistence (created automatically)
- **MQTT Configuration**: IoT features require MQTT broker connection
- **Supported models**: See `supported_models.txt` for the full list of available Gemini models

## Dependencies

**Core:**
- `Flask==3.0.3` - Web framework
- `google-generativeai==0.7.2` - Gemini API client
- `protobuf==4.25.4` - Protocol buffers

**IoT/Smart Home:**
- `paho-mqtt==1.6.1` - MQTT client for IoT device monitoring

**Utilities:**
- `pytz==2024.1` - Timezone support for time queries

## Features

### 1. Smart Home IoT Monitoring
- Real-time monitoring of Philio Z-Wave devices via MQTT
- Supported device types: Temperature sensors, Door/Window sensors, PIR motion sensors, Smart plugs
- Automatic temperature conversion (Fahrenheit → Celsius)
- Timestamp conversion (Unix → local time)
- Natural language queries in Chinese

### 2. Gemini Function Calling
- **get_smart_home_status**: Query IoT device status with filters
- **get_current_time**: Get current time with timezone support
- Automatic function detection and execution
- Context-aware error handling

### 3. Multi-User Chat Sessions
- Persistent chat history per user
- Automatic session restoration on server restart
- Background thread for history persistence

### 4. Production-Ready Deployment
- Docker support with multi-stage build
- Environment variable configuration
- Volume mounting for persistent data
- Graceful error handling

## Common Issues

1. **Server crashes on startup**:
   - Ensure `src/resources/system_instruction.txt` exists (should be auto-created)
   - Verify `API_KEY` environment variable is set
   - Check Python version is 3.10+

2. **MQTT connection fails**:
   - Verify `MQTT_BROKER_HOST` and `MQTT_BROKER_PORT` are correct
   - Check if MQTT broker is running and accessible
   - Server will still start but IoT features won't work

3. **Function calling errors**:
   - Check Gemini API version is up to date (`google-generativeai==0.7.2`)
   - Verify function declarations use `type_` (with underscore) not `type`
   - Check logs for function execution errors

4. **Import errors**:
   - Install all dependencies: `pip install -r requirements.txt`
   - Ensure working directory is `src/` when running server
   - Check virtual environment is activated

5. **Node.js examples not working**: Update Node.js to latest LTS version

6. **API errors**: Verify `API_KEY` environment variable is set correctly

## Coding Conventions

- **Main application**: All new development happens in `src/` directory
- **Legacy projects**: project_0, project_1, project_2 are for reference only
- **IoT integration**: Device handling code lives in `src/iot/`
- **Gemini integration**: AI/function calling logic in `src/gemini/`
- **Prefer small, incremental refactors**
- **Do not run tests or other commands unless explicitly requested**
- **Do not modify database schemas unless explicitly requested**
- **Use Chinese for user-facing messages** (system is designed for Chinese users)

## File Locations

- **System instructions**: `src/resources/system_instruction.txt`
- **Chat history**: `src/history/<user_id>`
- **Environment config**: `.env` (copy from `.env.example`)
- **Main server**: `src/server.py`
- **Gemini agent**: `src/gemini/agent.py`
- **MQTT client**: `src/iot/mqtt_client.py`
- **Docker config**: `Dockerfile` (project root)
- **Design notes**: `docs/Claude_generated/`
- **Reference data**: `docs/reference/` (IoT sample data, SDK specs)

