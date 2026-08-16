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
## System Workflow

StreamForge follows a real-time streaming architecture:

1. The Producer generates truck telemetry data.
2. Apache Kafka receives and streams the telemetry messages.
3. The Consumer reads messages from the Kafka topic.
4. The processing components handle the incoming stream data.
5. FastAPI exposes monitoring information through REST APIs.
6. The React dashboard displays the system and fleet information through a user-friendly interface.

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
## API Endpoints

The FastAPI backend provides the following endpoints:

| Endpoint | Description |
|---|---|
| `/` | Returns the backend status message |
| `/health` | Checks whether the backend is healthy |
| `/workers` | Returns worker information and status |
| `/partitions` | Returns Kafka partition assignments |
| `/metrics` | Returns streaming metrics such as events per second, lag, and uptime |
| `/topology` | Returns the StreamForge processing topology |
| `/logs` | Returns recent system activity logs |

FastAPI interactive documentation is available at:

```text
http://127.0.0.1:8000/docs

## Frontend

```bash
cd frontend
npm install
npm run dev
```