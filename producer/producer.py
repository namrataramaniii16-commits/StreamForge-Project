from confluent_kafka import Producer
import json
import random
import time
from datetime import datetime

def delivery_report(err, msg):
    if err is not None:
        print("Delivery failed:", err)
    else:
        print(f"Delivered to {msg.topic()} [{msg.partition()}]")

producer = Producer({
    'bootstrap.servers': 'localhost:9092'
})

while True:
    data = {
        "truck_id": f"TRUCK_{random.randint(1, 10):03}",
        "temperature": round(random.uniform(20, 40), 2),
        "timestamp": datetime.now().isoformat()
    }

    producer.produce(
        "truck-telemetry",
        json.dumps(data).encode("utf-8"),
        callback=delivery_report
    )

    producer.poll(0)
    producer.flush()

    print(f"Sent: {data}")

    time.sleep(2)