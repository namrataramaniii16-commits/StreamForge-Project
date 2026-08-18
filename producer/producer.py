import json
import random
import time
from datetime import datetime, timezone
from confluent_kafka import Producer

BOOTSTRAP_SERVER = "localhost:9092"
TOPIC_NAME = "truck-telemetry"

# Requirement: 50,000 trucks
TOTAL_TRUCKS = 50_000

# Normal demo rate
EVENTS_PER_SECOND = 1_000

producer = Producer({
    "bootstrap.servers": BOOTSTRAP_SERVER,
    "queue.buffering.max.messages": 1_000_000,
    "queue.buffering.max.kbytes": 1_048_576,
    "batch.num.messages": 10_000,
    "linger.ms": 5,
    "compression.type": "lz4",
})


def delivery_report(err, msg):
    if err:
        print(f"Delivery failed: {err}")


def create_event():
    truck_number = random.randint(1, TOTAL_TRUCKS)

    return {
        "truck_id": f"TRUCK_{truck_number:05d}",
        "temperature": round(random.uniform(-10.0, 45.0), 2),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


def main():
    print("=" * 60)
    print("StreamForge High Throughput Producer")
    print("=" * 60)
    print(f"Trucks       : {TOTAL_TRUCKS:,}")
    print(f"Target rate  : {EVENTS_PER_SECOND:,} events/sec")
    print(f"Topic        : {TOPIC_NAME}")
    print("=" * 60)

    interval = 1.0 / EVENTS_PER_SECOND
    sent = 0
    started = time.time()

    try:
        while True:
            event = create_event()

            # Kafka key ensures events for same truck go to same partition
            key = event["truck_id"].encode("utf-8")

            producer.produce(
                TOPIC_NAME,
                key=key,
                value=json.dumps(event).encode("utf-8"),
                callback=delivery_report,
            )

            producer.poll(0)

            sent += 1

            if sent % 10_000 == 0:
                elapsed = time.time() - started
                rate = sent / elapsed if elapsed else 0

                print(
                    f"Sent={sent:,} | "
                    f"Rate={rate:,.0f} events/sec"
                )

            # Demo throttling
            time.sleep(interval)

    except KeyboardInterrupt:
        print("\nStopping producer...")

    finally:
        producer.flush()
        print("Producer stopped.")


if __name__ == "__main__":
    main()