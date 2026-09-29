"""
collector.py - Client Subscribe MQTT, Validate JSON, Tinh Latency va Ghi vao InfluxDB
"""
import json
import os
import time
from datetime import datetime, timezone
from dotenv import load_dotenv
import paho.mqtt.client as mqtt
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS

load_dotenv()

MQTT_BROKER = os.getenv("MQTT_BROKER", "localhost")
MQTT_PORT = int(os.getenv("MQTT_PORT", 1883))
MQTT_TOPIC = os.getenv("MQTT_TOPIC", "sensor/dht22")

INFLUX_URL = os.getenv("INFLUXDB_URL", "http://localhost:8086")
INFLUX_TOKEN = os.getenv("INFLUXDB_TOKEN", "")
INFLUX_ORG = os.getenv("INFLUXDB_ORG", "ptit_iot")
INFLUX_BUCKET = os.getenv("INFLUXDB_BUCKET_RAW", "sensor_raw")

influx_client = None
write_api = None

def init_influx():
    global influx_client, write_api
    try:
        influx_client = InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN, org=INFLUX_ORG)
        write_api = influx_client.write_api(write_options=SYNCHRONOUS)
        print(f"[COLLECTOR] InfluxDB Client initialized for {INFLUX_URL} (Bucket: {INFLUX_BUCKET}) OK.", flush=True)
    except Exception as e:
        print(f"[COLLECTOR ERROR] Could not init InfluxDB client: {e}", flush=True)

def validate_payload(data):
    if not isinstance(data, dict):
        return False, "Payload is not a JSON object"
    
    required_keys = ["device_id", "timestamp"]
    for key in required_keys:
        if key not in data:
            return False, f"Missing required key: {key}"
            
    return True, "Valid"

def on_connect(client, userdata, flags, rc, properties=None):
    if rc == 0:
        print(f"[COLLECTOR] Connected to MQTT Broker! Subscribing to topic: {MQTT_TOPIC}", flush=True)
        client.subscribe(MQTT_TOPIC)
    else:
        print(f"[COLLECTOR ERROR] Connection failed, rc={rc}", flush=True)

def on_message(client, userdata, msg):
    recv_time = datetime.now(timezone.utc)
    payload_str = msg.payload.decode('utf-8')
    
    try:
        data = json.loads(payload_str)
        is_valid, reason = validate_payload(data)
        if not is_valid:
            print(f"[COLLECTOR WARNING] Invalid data ({reason}): {payload_str}", flush=True)
            return

        sent_time = datetime.fromisoformat(data["timestamp"])
        if sent_time.tzinfo is None:
            sent_time = sent_time.replace(tzinfo=timezone.utc)
            
        latency_ms = (recv_time - sent_time).total_seconds() * 1000.0

        device_id = data.get("device_id", "unknown")
        temp = data.get("temperature")
        hum = data.get("humidity")
        light = data.get("light")

        print(f"[REC] Dev:{device_id} | Temp:{temp}C | Hum:{hum}% | Light:{light} Lux | Latency:{latency_ms:.2f}ms", flush=True)

        if write_api:
            point = Point("environment_raw") \
                .tag("device_id", str(device_id)) \
                .field("latency_ms", float(latency_ms))

            if temp is not None and isinstance(temp, (int, float)):
                point = point.field("temperature", float(temp))
            if hum is not None and isinstance(hum, (int, float)):
                point = point.field("humidity", float(hum))
            if light is not None and isinstance(light, (int, float)):
                point = point.field("light", float(light))

            point = point.time(recv_time, WritePrecision.NS)
            write_api.write(bucket=INFLUX_BUCKET, record=point)

    except json.JSONDecodeError:
        print(f"[COLLECTOR ERROR] Could not decode JSON: {payload_str}", flush=True)
    except Exception as e:
        print(f"[COLLECTOR ERROR] Process message failed: {e}", flush=True)

def main():
    init_influx()

    try:
        client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="Collector_Subscriber")
    except AttributeError:
        client = mqtt.Client(client_id="Collector_Subscriber")

    client.on_connect = on_connect
    client.on_message = on_message

    try:
        print(f"[COLLECTOR] Connecting to MQTT Broker {MQTT_BROKER}:{MQTT_PORT}...", flush=True)
        client.connect(MQTT_BROKER, MQTT_PORT, 60)
        client.loop_forever()
    except KeyboardInterrupt:
        print("\n[COLLECTOR] Stopped Collector.", flush=True)
    except Exception as e:
        print(f"[COLLECTOR ERROR] {e}", flush=True)
    finally:
        if influx_client:
            influx_client.close()

if __name__ == "__main__":
    main()
