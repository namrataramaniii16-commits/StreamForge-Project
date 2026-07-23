# StreamForge

StreamForge is a scalable backend project that demonstrates real-time event streaming, asynchronous message processing, and containerized deployment using Python, Apache Kafka, and Docker.

## Features

- Real-time truck telemetry simulation
- Apache Kafka message streaming
- Dockerized Kafka deployment
- Kafka Producer for publishing telemetry data
- Kafka Consumer for reading telemetry data

## Tech Stack

- Python
- Apache Kafka
- Docker
- Confluent Kafka
- kafka-python

## Project Structure

StreamForge-Project/
├── docker/
├── producer/
├── consumer/
├── stream-processing/
├── backend/
├── dashboard/
├── requirements.txt
└── README.md

## Getting Started

### Clone the repository

git clone <repository-url>
cd StreamForge-Project

### Install dependencies

pip install -r requirements.txt

### Start Kafka

cd docker
docker compose up -d

### Run the Producer

python producer/producer.py

### Run the Consumer

python consumer/consumer.py

## Sample Output

### Producer

Sent: {'truck_id': 'TRUCK_001', 'temperature': 31.42}

### Consumer

Truck ID    : TRUCK_001
Temperature : 31.42 °C
Timestamp   : 2026-07-21T22:58:46