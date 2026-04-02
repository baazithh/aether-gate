import json
import random
import time
from kafka import KafkaProducer

producer = KafkaProducer(
    bootstrap_servers=['localhost:9092'],
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

def generate_transaction():
    # Purposely creating a mix of clean and "dirty" data
    is_dirty = random.random() < 0.3  # 30% chance of bad data
    
    return {
        "transaction_id": random.randint(1000, 9999),
        "user_email": "user@example.com" if not is_dirty else "EXPLOIT_SQL_INJECTION",
        "amount": random.uniform(10.0, 500.0),
        "currency": "USD" if not is_dirty else "INVALID_COIN",
        "timestamp": time.time()
    }

print("🚀 Aether-Gate Producer started. Sending data to Kafka...")
while True:
    data = generate_transaction()
    producer.send('raw_transactions', data)
    time.sleep(2) # Send a record every 2 seconds