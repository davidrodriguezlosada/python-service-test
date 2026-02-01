import signal
import sys
from contextlib import asynccontextmanager

from fastapi import FastAPI

from configuration.logger import configure_logging, get_logger
from configuration.settings import settings
from controller.products_controller import router as products_router
from event.kafka_consumer import start_kafka_consumer, stop_kafka_consumer

# Configure logging
configure_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle"""
    # Startup
    logger.info(
        "Application starting - %s, version: %s, environment: %s",
        settings.app_name,
        settings.app_version,
        settings.dd_env
    )
    
    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Start Kafka consumer
    start_kafka_consumer()
    
    yield  # Application runs here
    
    # Shutdown
    logger.info("Application shutting down")
    stop_kafka_consumer()


def signal_handler(signum, frame):
    """Handle shutdown signals"""
    logger.info("Shutdown signal received: %s", signum)
    stop_kafka_consumer()
    sys.exit(0)


# Patch libraries for Datadog tracing only if enabled
if settings.dd_enabled:
    from ddtrace import patch
    patch(fastapi=True, kafka=True)
    logger.info("Datadog tracing enabled")
else:
    logger.info("Datadog tracing disabled")

# Create FastAPI app with lifespan
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Python service with XML logging and Kafka integration",
    lifespan=lifespan
)

# Include routers with prefix for better tracing
app.include_router(products_router, tags=["products"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )
