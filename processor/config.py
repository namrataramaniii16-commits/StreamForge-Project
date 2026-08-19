"""
StreamForge processor configuration.
"""

KAFKA_BROKER = "localhost:9092"

INPUT_TOPIC = "truck-telemetry"

CHANGELOG_TOPIC = "streamforge-changelog"

CONSUMER_GROUP = "streamforge-workers"

APP_NAME = "streamforge-processor"

# Requirement: 5-minute window
WINDOW_SIZE_MS = 5 * 60 * 1000

# Requirement: 20 workers
TOTAL_WORKERS = 20

# Processor metrics server
METRICS_PORT = 8001