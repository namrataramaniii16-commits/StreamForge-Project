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