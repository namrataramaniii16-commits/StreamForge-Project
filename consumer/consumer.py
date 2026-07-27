from kafka import KafkaConsumer
import json

consumer = KafkaConsumer(
    "truck-telemetry",
    bootstrap_servers="localhost:9092",
    auto_offset_reset="earliest",
    enable_auto_commit=True,
    value_deserializer=lambda x: json.loads(x.decode("utf-8"))
)

print("Listening for truck telemetry data...\n")

for message in consumer:
    data = message.value

    print("=" * 40)
    print(f"Truck ID    : {data['truck_id']}")
    print(f"Temperature : {data['temperature']} °C")
    print(f"Timestamp   : {data['timestamp']}")
    print("=" * 40)