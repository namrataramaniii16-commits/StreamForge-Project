"""
Configuration settings for the StreamForge Processor.
This file stores all configurable values used by the Faust application.
"""

# Kafka Configuration
KAFKA_BROKER = "localhost:9092"
INPUT_TOPIC = "truck-telemetry"

# Faust Configuration
APP_NAME = "streamforge-processor"
CONSUMER_GROUP = "streamforge-processor"