import json
import asyncio
from aiokafka import AIOKafkaConsumer
from redis import Redis

# Use a unique group ID to avoid the Kafka Error 15
GROUP_ID = "gatekeeper-v3-final" 

# Connect to Redis
redis_client = Redis(host='localhost', port=6379, db=0, decode_responses=True)

async def start_gatekeeper():
    consumer = AIOKafkaConsumer(
        'raw_transactions',
        bootstrap_servers='localhost:9092',
        group_id=GROUP_ID,
        auto_offset_reset="earliest",
        retry_backoff_ms=500
    )
    
    # Retry loop to handle Kafka startup lag
    connected = False
    while not connected:
        try:
            await consumer.start()
            connected = True
            print("🚀 Aether-Gate Lineage Consumer Started...")
        except Exception as e:
            print(f"🔄 Waiting for Kafka Coordinator... {e}")
            await asyncio.sleep(2)

    try:
        async for msg in consumer:
            data = json.loads(msg.value)
            
            # Logic: Check for anomalies
            if data.get('currency') == "INVALID_COIN" or "EXPLOIT" in data.get('user_email', ''):
                print(f"⚠️ INTERVENTION REQUIRED: Transaction {data['transaction_id']}")
                redis_client.setex(f"intervention:{data['transaction_id']}", 3600, json.dumps(data))
            else:
                print(f"✅ CLEAN DATA: {data['transaction_id']} Routing to Iceberg...")
    finally:
        await consumer.stop()