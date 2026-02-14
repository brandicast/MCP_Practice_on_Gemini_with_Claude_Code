"""
MQTT Client for Philio Z-Wave IoT Device Monitoring
Subscribes to MQTT topics and maintains real-time device status
"""

import os
import json
import threading
import time
import logging
import paho.mqtt.client as mqtt
from datetime import datetime

logger = logging.getLogger(__name__)

# Thread-safe device status cache
iot_devices_status = {}
iot_status_lock = threading.Lock()
mqtt_connected = False

# MQTT Configuration from environment variables
MQTT_BROKER_HOST = os.environ.get('MQTT_BROKER_HOST', 'localhost')
MQTT_BROKER_PORT = int(os.environ.get('MQTT_BROKER_PORT', '1883'))
MQTT_USERNAME = os.environ.get('MQTT_USERNAME', '')
MQTT_PASSWORD = os.environ.get('MQTT_PASSWORD', '')
MQTT_TOPIC = os.environ.get('topic_for_iot', 'brandon/iot/zwave/philio/event/#')

# ========== Philio Product Code Mappings ==========
PRODUCT_CODE_MAP = {
    "00000000": "N/A",
    "01010000": "Philio All Switch",
    "01010001": "Philio Sun Rise",
    "01010002": "Philio Sun Set",
    "01010003": "Philio Scene Status",
    "01010004": "Philio Timer",
    "0101020C": "Philio PST02-A 4 in 1 Multi-Sensor",
    "0101020D": "Philio PST02-B PIR Motion Sensor",
    "0101020E": "Philio PST02-C Door/Window Contact Detector",
    "0101010F": "Philio PAN03 Switch Module",
    "01010128": "Philio PAN15 Smart Energy Plug-in Switch",
    "FFFFFFFF": "Not Available"
}

# ========== Function Type Mappings (62 types) ==========
FUNCTION_TYPE_MAP = {
    0: "N/A",
    11: "Temperature Sensor",
    12: "Illumination Sensor",
    13: "Door / Window Sensor",
    14: "PIR Sensor",
    15: "Humidity Sensor",
    16: "GPIO",
    17: "Smoke Sensor",
    18: "CO Sensor",
    19: "CO2 Sensor",
    20: "Flood Sensor",
    21: "Glass Break Sensor",
    22: "Meter Switch",
    23: "Switch",
    24: "Dimmer",
    25: "Siren",
    26: "Curtain",
    27: "Remote",
    28: "Button",
    29: "Meter Sensor",
    30: "Meter Dimmer",
    31: "Door Lock",
    32: "Thermostat Fan",
    33: "Thermostat Mode",
    34: "Thermostat Temperature",
    35: "Remote Control",
    36: "Valve Switch",
    37: "Air Sensor",
    40: "UV Sensor",
    41: "Color Dimmer",
    42: "Sunrise(PS)",
    43: "Sunset(PS)",
    44: "Scene Status",
    45: "Door Lock Sensor",
    46: "Timer",
    49: "Heat Sensor",
    50: "Keypad",
    51: "PM Sensor",
    52: "Gas Meter",
    100: "Repeater"
}

# ========== Event Code Mappings (Key events) ==========
EVENT_CODE_MAP = {
    # Device Management
    1002: "Device included",
    1003: "Device removed",
    4003: "Battery Change",
    5010: "DEVICE WAKEUP",

    # Triggers
    4001: "Tamper trigger",
    4002: "Low battery",
    4101: "PIR trigger",
    4102: "Door/window open",
    4103: "Door/window close",
    4104: "Smoke trigger",
    4105: "CO trigger",
    4106: "CO2 trigger",
    4107: "Flood trigger",
    4108: "Glass break",

    # Reports
    4801: "Temperature report",
    4802: "Illumination report",
    4803: "Humidity report",
    4804: "Meter report",
    4805: "CO2 report",
    4806: "VOC report",
    4808: "PM report",
    4809: "Gas report",

    # Status
    5001: "Status off",
    5002: "Status update",
    5003: "CONFIG_CHANGE"
}


def convert_product_code_to_hex(product_code):
    """Convert decimal product code to hex format for lookup"""
    try:
        hex_code = format(product_code, '08X')
        return hex_code
    except Exception as e:
        logger.error(f"Error converting product code {product_code}: {e}")
        return "00000000"


def get_product_name(product_code):
    """Get product name from product code"""
    hex_code = convert_product_code_to_hex(product_code)
    return PRODUCT_CODE_MAP.get(hex_code, f"Unknown Product (0x{hex_code})")


def get_function_type_description(func_type):
    """Get function type description"""
    return FUNCTION_TYPE_MAP.get(func_type, f"Unknown Function Type {func_type}")


def get_event_description(event_code):
    """Get event description"""
    return EVENT_CODE_MAP.get(event_code, f"Unknown Event {event_code}")


def convert_temperature_to_celsius(sensor_value):
    """
    Convert temperature from Fahrenheit (tenths) to Celsius
    sensor_value: 710 = 71.0°F
    Returns: 21.7°C
    """
    try:
        fahrenheit = sensor_value / 10.0
        celsius = (fahrenheit - 32) * 5 / 9
        return round(celsius, 1)
    except Exception as e:
        logger.error(f"Error converting temperature {sensor_value}: {e}")
        return 0.0


def clean_device_name(name):
    """Strip non-printable characters from device name"""
    if not name:
        return ""
    return ''.join(char for char in name if char.isprintable()).strip()


def convert_timestamp_to_local_time(timestamp):
    """
    Convert Unix timestamp to local time string

    Args:
        timestamp: Unix timestamp (seconds since epoch)

    Returns:
        str: Local time in format "YYYY-MM-DD HH:MM:SS"
    """
    try:
        dt = datetime.fromtimestamp(timestamp)
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except Exception as e:
        logger.error(f"Error converting timestamp {timestamp}: {e}")
        return "Unknown time"


def on_connect(client, userdata, flags, rc):
    """Callback when connected to MQTT broker"""
    global mqtt_connected
    if rc == 0:
        mqtt_connected = True
        logger.info("Connected to MQTT broker successfully")
        # Subscribe to topic
        client.subscribe(MQTT_TOPIC)
        logger.info(f"Subscribed to topic: {MQTT_TOPIC}")
    else:
        mqtt_connected = False
        logger.error(f"Failed to connect to MQTT broker, return code: {rc}")


def on_disconnect(client, userdata, rc):
    """Callback when disconnected from MQTT broker"""
    global mqtt_connected
    mqtt_connected = False
    if rc != 0:
        logger.warning(f"Unexpected MQTT disconnection. Will auto-reconnect. RC: {rc}")


def on_message(client, userdata, msg):
    """
    Callback when MQTT message received
    Message format is direct JSON payload (not wrapped with topic key)
    """
    try:
        # Parse JSON payload directly
        event_data = json.loads(msg.payload.decode('utf-8'))
        # logger.debug(f"Received MQTT message on topic {msg.topic}: {event_data}")

        # Validate it's a dict with required fields
        if not isinstance(event_data, dict):
            logger.warning(f"Payload is not a dict: {type(event_data)}")
            return

        if 'productCode' not in event_data or 'funcType' not in event_data:
            logger.debug(f"Missing required fields in event: {event_data.keys()}")
            return

        # Extract core fields
        product_code = event_data.get('productCode', 0)
        func_type = event_data.get('funcType', 0)
        event_code = event_data.get('eventCode', 0)
        sensor_value = event_data.get('sensorValue', 0)

        # Create unique device ID
        device_id = f"{product_code}_{func_type}"

        # Get descriptive names
        product_hex = convert_product_code_to_hex(product_code)
        device_name = get_product_name(product_code)
        func_type_desc = get_function_type_description(func_type)
        event_desc = get_event_description(event_code)

        # Clean user-defined name
        user_name = clean_device_name(event_data.get('funcName', ''))

        # Get timestamp and convert to local time
        timestamp = event_data.get('timeStamp', int(time.time()))
        local_time = convert_timestamp_to_local_time(timestamp)

        # Build device status object
        device_status = {
            'device_id': device_id,
            'product_code': product_code,
            'product_hex': product_hex,
            'device_name': device_name,
            'user_name': user_name,
            'func_type': func_type,
            'func_type_description': func_type_desc,
            'event_code': event_code,
            'event_description': event_desc,
            'sensor_value_raw': sensor_value,
            'data_unit': event_data.get('dataUnit', 0),
            'battery': event_data.get('battery', 100),
            'basic_value': event_data.get('basicValue', 0),
            'timestamp': timestamp,
            'local_time': local_time,
            'uid': event_data.get('UID', 0),
            'channel_id': event_data.get('channelId', 0),
            'mqtt_topic': msg.topic,
            'meter': event_data.get('meter', None)
        }

        # Temperature conversion for temperature sensors
        if func_type == 11 and event_code == 4801:  # Temperature Sensor + Temperature report
            celsius = convert_temperature_to_celsius(sensor_value)
            device_status['temperature_celsius'] = celsius
            logger.debug(f"Temperature conversion: {sensor_value} raw → {sensor_value/10.0}°F → {celsius}°C")
        else:
            device_status['temperature_celsius'] = None

        # Thread-safe update to global status
        with iot_status_lock:
            iot_devices_status[device_id] = device_status

        logger.debug(f"Updated device {device_id} ({device_name}) - {user_name}: {event_desc}")

    except json.JSONDecodeError as e:
        logger.error(f"Failed to decode JSON from topic {msg.topic}: {e}")
    except Exception as e:
        logger.error(f"Error processing MQTT message: {e}", exc_info=True)


def start_mqtt_client():
    """Start MQTT client in background thread"""
    try:
        client = mqtt.Client()

        # Set callbacks
        client.on_connect = on_connect
        client.on_disconnect = on_disconnect
        client.on_message = on_message

        # Set credentials if provided
        if MQTT_USERNAME and MQTT_PASSWORD:
            client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)

        # Connect to broker
        logger.info(f"Connecting to MQTT broker at {MQTT_BROKER_HOST}:{MQTT_BROKER_PORT}")
        client.connect(MQTT_BROKER_HOST, MQTT_BROKER_PORT, 60)

        # Start network loop (blocking)
        client.loop_forever()

    except Exception as e:
        logger.error(f"MQTT client error: {e}", exc_info=True)


def get_iot_status(device_name=None, user_name=None, device_type=None, event_type=None):
    """
    Query IoT device status with optional filters

    Args:
        device_name: Product name filter (partial match, e.g., "PST02-A")
        user_name: User-defined name filter (partial match, e.g., "五樓")
        device_type: Function type filter (partial match, e.g., "Temperature Sensor")
        event_type: Event description filter (partial match, e.g., "Temperature report")

    Returns:
        dict: {
            'mqtt_connected': bool,
            'devices': list of matching device objects,
            'total_count': int
        }
    """
    with iot_status_lock:
        # Check if we have any data
        if not iot_devices_status:
            return {
                'error': 'No IoT device data available yet',
                'mqtt_connected': mqtt_connected,
                'devices': [],
                'total_count': 0
            }

        # Start with all devices
        filtered_devices = list(iot_devices_status.values())

        # Apply filters (case-insensitive partial matching)
        if device_name:
            device_name_lower = device_name.lower()
            filtered_devices = [
                d for d in filtered_devices
                if device_name_lower in d['device_name'].lower()
            ]

        if user_name:
            user_name_lower = user_name.lower()
            filtered_devices = [
                d for d in filtered_devices
                if user_name_lower in d['user_name'].lower()
            ]

        if device_type:
            device_type_lower = device_type.lower()
            filtered_devices = [
                d for d in filtered_devices
                if device_type_lower in d['func_type_description'].lower()
            ]

        if event_type:
            event_type_lower = event_type.lower()
            filtered_devices = [
                d for d in filtered_devices
                if event_type_lower in d['event_description'].lower()
            ]

        return {
            'mqtt_connected': mqtt_connected,
            'devices': filtered_devices,
            'total_count': len(filtered_devices)
        }


# ========== MQTT Background Thread Startup ==========
def start_mqtt_subscriber():
    """Start MQTT subscriber in background thread"""
    mqtt_thread = threading.Thread(target=start_mqtt_client, daemon=True)
    mqtt_thread.start()
    logger.info("MQTT subscriber thread started for Philio IoT devices")


# Auto-start MQTT subscriber when module is imported
start_mqtt_subscriber()
