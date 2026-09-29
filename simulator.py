"""
simulator.py - Mo phong thiet bi cam bien IoT (ESP32/DHT22+LDR)
Publish du lieu JSON qua MQTT Broker
"""
import time
import json
import random
from datetime import datetime, timezone
import os
from dotenv import load_dotenv
import paho.mqtt.client as mqtt

load_dotenv()

MQTT_BROKER = os.getenv("MQTT_BROKER", "localhost")
MQTT_PORT = int(os.getenv("MQTT_PORT", 1883))
MQTT_TOPIC = os.getenv("MQTT_TOPIC", "sensor/dht22")

DEVICE_ID = "esp32_sensor_01"

def generate_sensor_data():
    base_temp = 28.0 + random.uniform(-2.0, 2.0)
    base_hum = 65.0 + random.uniform(-5.0, 5.0)
    base_light = 550.0 + random.uniform(-50.0, 50.0)

    # 5% co hoi tao Outlier ngau nhien
    if random.random() < 0.05:
        base_temp += random.choice([50.0, -30.0])
    
    # 5% co hoi khuyet gia tri (Missing Value)
    hum_val = None if random.random() < 0.05 else round(base_hum, 2)

    payload = {
        "device_id": DEVICE_ID,
        "temperature": round(base_temp, 2),
        "humidity": hum_val,
        "light": round(base_light, 2),
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    return payload

def main():
    try:
        client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="Simulator_Publisher")
    except AttributeError:
        client = mqtt.Client(client_id="Simulator_Publisher")

    try:
        print(f"[SIMULATOR] Connecting to MQTT Broker {MQTT_BROKER}:{MQTT_PORT}...", flush=True)
        client.connect(MQTT_BROKER, MQTT_PORT, 60)
        client.loop_start()
        print(f"[SIMULATOR] Connected! Publishing data to topic: '{MQTT_TOPIC}'...", flush=True)

        count = 0
        while True:
            data = generate_sensor_data()
            json_payload = json.dumps(data)
            client.publish(MQTT_TOPIC, json_payload)
            count += 1
            print(f"[{count}] Published: {json_payload}", flush=True)
            time.sleep(1)

    except KeyboardInterrupt:
        print("\n[SIMULATOR] Stopped.", flush=True)
    except Exception as e:
        print(f"[SIMULATOR ERROR] {e}", flush=True)
    finally:
        client.loop_stop()
        client.disconnect()

if __name__ == "__main__":
    main()
