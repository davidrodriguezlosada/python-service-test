# Python Service Test

Python service with ECS JSON logging, Kafka integration, and Datadog monitoring.

## Features

- **FastAPI** web framework with async support
- **ECS JSON structured logging** with structlog and ecs-logging
- **Kafka consumer** for message processing
- **Datadog APM** with ddtrace for metrics and tracing
- **Health check** endpoints
- **Configuration management** with Pydantic

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Copy environment configuration:
```bash
cp .env.example .env
```

3. Configure your Kafka and Datadog settings in `.env`

4. Run the service:
```bash
python src/main.py
```

## Endpoints

- `GET /products` - Endpoint that logs API calls and returns a list of products
- `GET /health` - Health check endpoint

## Kafka Integration

The service automatically starts a Kafka consumer that:
- Listens to topic configured in `KAFKA_TOPIC`
- Logs each message
- Includes Datadog tracing for message processing

## Datadog Monitoring

Ensure Datadog Agent is running and accessible at `localhost:8126`. The service will automatically:
- Send traces to Datadog
- Instrument FastAPI endpoints
- Instrument Kafka operations
- Include service metadata in traces

## Logging

Logs are output in ECS JSON format (or text/xml depending on configuration) with structured data including:
- Timestamp
- Log level
- Service name
- Environment
- Event-specific metadata
- Custom tags (env, application, solution, service, domain, version)

## Docker Setup

### Start Kafka and Datadog Agent:
```bash
# Copy environment file
cp .env.docker .env

# Start services
docker-compose up -d

# View logs
docker-compose logs -f
```

### Services included:
- **Kafka** on `localhost:9092`
- **Zookeeper** on `localhost:2181`
- **Kafka UI** on `http://localhost:8080`
- **Datadog Agent** on `localhost:8126`

### Stop services:
```bash
docker-compose down
```

## Testing

Send a request to test:
```bash
curl http://localhost:8000/products
```

Send a message to Kafka topic:
```bash
# Using docker exec
docker exec -it kafka kafka-console-producer.sh --broker-list localhost:9092 --topic test-topic

# Or use kafka-ui at http://localhost:8080
```
