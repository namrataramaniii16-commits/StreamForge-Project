"""
Main entry point for the StreamForge Stream Processing module.
"""

from config import KAFKA_BROKER, INPUT_TOPIC, CONSUMER_GROUP


def main():
    print("===================================")
    print(" StreamForge Stream Processor")
    print("===================================")
    print(f"Kafka Broker : {KAFKA_BROKER}")
    print(f"Input Topic  : {INPUT_TOPIC}")
    print(f"Consumer Group : {CONSUMER_GROUP}")
    print("\nProcessor initialized successfully.")


if __name__ == "__main__":
    main()