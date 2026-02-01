#!/usr/bin/env python3
"""Simple test script to publish a message to Kafka"""

import json
import time
from kafka import KafkaProducer
from configuration.settings import settings

def test_producer():
    """Test publishing a message to Kafka"""
    print(f"Connecting to Kafka: {settings.kafka_bootstrap_servers}")
    print(f"Topic: {settings.kafka_topic}")
    
    try:
        producer = KafkaProducer(
            bootstrap_servers=settings.kafka_bootstrap_servers,
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
            key_serializer=lambda k: k.encode('utf-8') if k else None
        )
        
        # Test message
        test_message = {
            "event": "test_message",
            "timestamp": time.time(),
            "data": "Hello Kafka!",
            "source": "test_producer"
        }
        
        print(f"Sending message: {test_message}")
        
        # Send message
        future = producer.send(
            settings.kafka_topic,
            key="test_key",
            value=test_message
        )
        
        # Wait for the message to be sent
        record_metadata = future.get(timeout=10)
        
        print("Message sent successfully!")
        print(f"Topic: {record_metadata.topic}")
        print(f"Partition: {record_metadata.partition}")
        print(f"Offset: {record_metadata.offset}")
        
        producer.flush()
        producer.close()
        
    except Exception as e:
        print(f"Error sending message: {e}")

if __name__ == "__main__":
    test_producer()
