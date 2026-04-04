import json
import asyncio
from aiokafka import AIOKafkaConsumer
from redis import Redis

# IMPORTANT: Use a brand new Group ID to bypass stuck metadata
GROUP_ID = "gatekeeper-v10-final" 

redis_client = Redis(host='localhost', port=6379, db=0, decode_responses=True)

async def start_gatekeeper():
    consumer = AIOKafkaConsumer(
        'raw_transactions',
        bootstrap_servers='localhost:9092',
        group_id=GROUP_ID,
        auto_offset_reset="earliest",
        retry_backoff_ms=1000  # Wait 1s between retries
    )
    
    # This loop forces the 'Handshake' with the Broker
    while True:
        try:
            await consumer.start()
            print("🚀 Aether-Gate Lineage Consumer Started...")
            break
        except Exception as e:
            # This captures the 'Error 15' and keeps trying until Kafka is ready
            print(f"🔄 Waiting for Kafka Coordinator... {e}")
            await asyncio.sleep(2)

    try:
        async for msg in consumer:
            data = json.loads(msg.value)
            if data.get('currency') == "INVALID_COIN" or "EXPLOIT" in data.get('user_email', ''):
                print(f"⚠️ INTERVENTION: {data['transaction_id']}")
                redis_client.setex(f"intervention:{data['transaction_id']}", 3600, json.dumps(data))
            else:
                print(f"✅ CLEAN: {data['transaction_id']}")
    finally:
        await consumer.stop()