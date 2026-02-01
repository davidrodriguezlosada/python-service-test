import threading

from kafka import KafkaConsumer

from configuration.settings import settings
from configuration.logger import get_logger

logger = get_logger(__name__)

# Global consumer reference
consumer_thread = None
shutdown_event = threading.Event()


def kafka_consumer_worker():
    """Kafka consumer that logs messages"""
    logger.info(
        "Starting Kafka consumer - topic: %s, group_id: %s, servers: %s",
        settings.kafka_topic,
        settings.kafka_consumer_group,
        settings.kafka_bootstrap_servers
    )
    
    try:
        consumer = KafkaConsumer(
            settings.kafka_topic,
            bootstrap_servers=settings.kafka_bootstrap_servers,
            group_id=settings.kafka_consumer_group,
            auto_offset_reset='earliest',
            enable_auto_commit=True,
            value_deserializer=lambda m: m.decode('utf-8')
        )
        
        logger.info("Kafka consumer created successfully - topics: %s, bootstrap_servers: %s", 
                   consumer.subscription(),
                   settings.kafka_bootstrap_servers)
        
    except Exception as e:
        logger.error("Failed to create Kafka consumer: %s", str(e))
        return
    
    try:
        message_count = 0
        while not shutdown_event.is_set():
            logger.debug("Polling for messages...")
            message_batch = consumer.poll(timeout_ms=1000)
            
            if not message_batch:
                logger.debug("No messages received in this poll")
                continue
            
            logger.info("Received message batch: %d messages", len(message_batch))
            
            for topic_partition, messages in message_batch.items():
                logger.info("Processing messages for topic partition - topic: %s, partition: %d, message_count: %d", 
                           topic_partition.topic, 
                           topic_partition.partition,
                           len(messages))
                
                for message in messages:
                    message_count += 1
                    logger.info(
                        "Kafka message received - #%d, topic: %s, partition: %d, offset: %d, key: %s, value: %s, timestamp: %d",
                        message_count,
                        message.topic,
                        message.partition,
                        message.offset,
                        message.key,
                        message.value,
                        message.timestamp
                    )
                            
    except Exception as e:
        logger.error("Kafka consumer error: %s", str(e))
    finally:
        consumer.close()
        logger.info("Kafka consumer stopped")


def start_kafka_consumer():
    """Start Kafka consumer in background thread"""
    global consumer_thread
    
    consumer_thread = threading.Thread(target=kafka_consumer_worker, daemon=True)
    consumer_thread.start()
    logger.info("Kafka consumer thread started")


def stop_kafka_consumer():
    """Stop Kafka consumer"""
    logger.info("Stopping Kafka consumer")
    shutdown_event.set()
    if consumer_thread:
        consumer_thread.join(timeout=5)
