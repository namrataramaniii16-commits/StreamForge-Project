# StreamForge

StreamForge is a scalable backend project that demonstrates real-time event streaming, asynchronous message processing, and containerized deployment using Python, Apache Kafka, Docker, FastAPI, and React.

## Features

- Real-time truck telemetry simulation
- Apache Kafka message streaming
- Dockerized Kafka deployment
- Kafka Producer for publishing telemetry data
- Kafka Consumer for reading telemetry data
- FastAPI backend APIs
- React monitoring dashboard

## Problem Statement

Modern transportation systems generate a large amount of real-time telemetry data from vehicles, including location, speed, fuel level, temperature, and operational status. Processing and monitoring this continuously generated data can become difficult when using traditional request-based systems.

StreamForge addresses this problem by providing a real-time event streaming and monitoring system. Truck telemetry data is published through Apache Kafka, consumed and processed asynchronously, and exposed through FastAPI APIs. A React-based dashboard provides a centralized interface for monitoring the system and viewing real-time operational information.

The project demonstrates how a distributed streaming architecture can be used to handle continuous event data efficiently while providing APIs and a monitoring interface for users.

## Tech Stack

- Python
- Apache Kafka
- Docker
- FastAPI
- React
- Confluent Kafka
- kafka-python

## Project Structure

```
StreamForge-Project/
├── app/
├── frontend/
├── docker/
├── producer/
├── consumer/
├── processing/
├── processor/
├── docs/
├── requirements.txt
└── README.md
```

## Installation

```bash
pip install -r requirements.txt
```

## Start Kafka

```bash
cd docker
docker compose up -d
```

## Run Producer

```bash
python producer/producer.py
```

## Run Consumer

```bash
python consumer/consumer.py
```

## Run FastAPI

```bash
uvicorn app.main:app --reload
```

Open:

```
http://127.0.0.1:8000/docs
```

## Frontend

```bash
cd frontend
npm install
npm run dev
```