import asyncio
import json
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from redis import Redis
from .kafka_consumer import start_gatekeeper

# Connect to Dockerized Redis (decode_responses=True for clean strings)
redis_client = Redis(host='localhost', port=6379, db=0, decode_responses=True)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Handles the startup and shutdown of the Aether-Gate background tasks.
    """
    print("⏳ Awaiting Kafka Broker stability (5s)...")
    # This delay is the "secret sauce" to avoid the GroupCoordinator loop on Arch
    await asyncio.sleep(5) 
    
    # Start the Kafka listener from your kafka_consumer.py as a background task
    task = asyncio.create_task(start_gatekeeper())
    
    yield
    
    print("🛑 Shutting down Aether-Gate Consumer...")
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        print("✅ Background task closed safely.")

app = FastAPI(
    title="Aether-Gate API",
    description="The 'Human-in-the-loop' Gateway for Medallion Architecture",
    lifespan=lifespan
)

# CORS Configuration for your Next.js Surgery Suite
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """System Heartbeat Check"""
    try:
        redis_status = redis_client.ping()
    except:
        redis_status = False
        
    return {
        "status": "Aether-Gate is Breathing", 
        "system": "Arch Linux",
        "redis_connected": redis_status
    }

@app.get("/pending-interventions")
async def get_pending():
    """Fetch 'Dirty' records trapped in the Redis Waiting Room"""
    keys = redis_client.keys("intervention:*")
    
    items = []
    for k in keys:
        raw_data = redis_client.get(k)
        if raw_data:
            # Parse the string back into a JSON object for the frontend
            items.append(json.loads(raw_data))
            
    return {
        "count": len(items), 
        "items": items
    }

@app.post("/intervene/{transaction_id}")
async def submit_intervention(transaction_id: str, corrected_data: dict):
    """
    Manually 'Promotes' a fixed record. 
    Removes it from the Redis queue after you click 'Fix & Route' in the UI.
    """
    result = redis_client.delete(f"intervention:{transaction_id}")
    
    if result:
        print(f"🛠️ MANUAL FIX APPLIED: TX_{transaction_id}")
        # In the next phase, we'll add the Spark/Iceberg write here
        return {"status": "success", "message": f"Transaction {transaction_id} promoted to Gold."}
    
    return {"status": "error", "message": "Transaction not found or already processed."}