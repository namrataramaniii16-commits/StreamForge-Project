from confluent_kafka import Producer
import json
import random
import time
from datetime import datetime

# Kafka Configuration
BOOTSTRAP_SERVER = "localhost:9092"
TOPIC_NAME = "truck-telemetry"
SEND_INTERVAL = 2  # seconds

producer = Producer({
    "bootstrap.servers": BOOTSTRAP_SERVER
})


def delivery_report(err, msg):
    """Callback to report message delivery status."""
    if err is not None:
        print(f"❌ Delivery failed: {err}")
    else:
        print(f"✅ Delivered to {msg.topic()} [Partition {msg.partition()}]")


print("Starting Kafka Producer...")
print(f"Publishing data to topic: {TOPIC_NAME}\n")

try:
    while True:
        data = {
            "truck_id": f"TRUCK_{random.randint(1, 10):03}",
            "temperature": round(random.uniform(20, 40), 2),
            "timestamp": datetime.now().isoformat()
        }

        producer.produce(
            TOPIC_NAME,
            json.dumps(data).encode("utf-8"),
            callback=delivery_report
        )

        producer.poll(0)
        producer.flush()

        print(f"📤 Sent: {data}")

        time.sleep(SEND_INTERVAL)

except KeyboardInterrupt:
    print("\nStopping producer...")

finally:
    producer.flush()
    print("Producer closed successfully.")