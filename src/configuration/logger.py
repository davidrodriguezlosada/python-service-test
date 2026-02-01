import logging
import json

import structlog
from ecs_logging import StdlibFormatter

from .settings import settings


class ECSTagsFormatter(StdlibFormatter):
    """Custom ECS formatter with tags field"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tags = {
            "env": settings.tags_env,
            "trace": settings.tags_trace,
            "application": settings.tags_application,
            "solution": settings.tags_solution,
            "service": settings.tags_service,
            "domain": settings.tags_domain,
            "version": settings.tags_version
        }
    
    def format(self, record):
        # Get the base ECS formatted log
        log_record = super().format(record)
        
        # Parse the JSON and add tags
        try:
            log_dict = json.loads(log_record)
            log_dict["tags"] = self.tags
            return json.dumps(log_dict)
        except (json.JSONDecodeError, TypeError):
            # Fallback if JSON parsing fails
            return log_record


def configure_logging():
    """Configure structured logging with ECS output"""
    
    # Configure stdlib logging based on format
    handler = logging.StreamHandler()
    
    if settings.log_format.lower() == "ecs":
        handler.setFormatter(ECSTagsFormatter())
    elif settings.log_format.lower() == "text":
        # Plain text format with timestamp and level
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
    else:
        # Default to simple format for xml/json
        formatter = logging.Formatter(
            '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
        )
        handler.setFormatter(formatter)
    
    # Configure root logger - ALL loggers inherit this
    root_logger = logging.getLogger()
    root_logger.handlers = []
    root_logger.addHandler(handler)
    root_logger.setLevel(getattr(logging, settings.log_level.upper()))
    
    # Suppress noisy loggers
    noisy_loggers = ["urllib3.connectionpool", "boto3", "botocore", "kafka"]
    for logger_name in noisy_loggers:
        logging.getLogger(logger_name).setLevel(logging.WARNING)
    
    # Configure structlog only for structured formats
    if settings.log_format.lower() != "text":
        structlog.configure(
            processors=[
                structlog.stdlib.filter_by_level,
                structlog.stdlib.add_logger_name,
                structlog.stdlib.add_log_level,
                structlog.stdlib.PositionalArgumentsFormatter(),
                structlog.processors.TimeStamper(fmt="iso"),
                structlog.processors.StackInfoRenderer(),
                structlog.processors.format_exc_info,
                structlog.processors.UnicodeDecoder(),
                structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
            ],
            context_class=dict,
            logger_factory=structlog.stdlib.LoggerFactory(),
            wrapper_class=structlog.stdlib.BoundLogger,
            cache_logger_on_first_use=True,
        )


def get_logger(name: str = None):
    """Get a logger instance based on format"""
    if settings.log_format.lower() == "text":
        # Return standard Python logger for text format
        return logging.getLogger(name or settings.app_name)
    else:
        # Return structlog logger for structured formats
        return structlog.get_logger(name or settings.app_name)
