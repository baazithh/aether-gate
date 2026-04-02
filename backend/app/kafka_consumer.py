import json
from aiokafka import AIOKafkaConsumer
from redis import Redis

redis_client = Redis(host='localhost', port=6379, db=0)

async def start_gatekeeper():
    consumer = AIOKafkaConsumer(
        'raw_transactions',
        bootstrap_servers='localhost:9092',
        group_id="gatekeeper-group"
    )
    await consumer.start()
    try:
        async for msg in consumer:
            data = json.loads(msg.value)
            
            # THE LOGIC: Check for "Dirty" data
            if data['currency'] == "INVALID_COIN" or "EXPLOIT" in data['user_email']:
                print(f"⚠️ INTERVENTION REQUIRED: Transaction {data['transaction_id']}")
                # Store in Redis for the UI to pick up
                redis_client.set(f"intervention:{data['transaction_id']}", json.dumps(data))
            else:
                print(f"✅ CLEAN DATA: Routing to Iceberg...")
                # In the next step, we'll write the Iceberg sink here
    finally:
        await consumer.stop()