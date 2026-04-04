import asyncio
import json
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from redis import Redis
from .kafka_consumer import start_gatekeeper

# Connect to Dockerized Redis
# decode_responses=True ensures we get clean strings for the Next.js UI
redis_client = Redis(host='localhost', port=6379, db=0, decode_responses=True)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Handles the startup and shutdown of the Aether-Gate background tasks.
    """
    print("⏳ Awaiting Kafka Broker stability (5s)...")
    await asyncio.sleep(5)  # Crucial: Gives the Group Coordinator time to elect a leader
    
    # Start the Kafka listener as a background task
    task = asyncio.create_task(start_gatekeeper())
    print("🚀 Aether-Gate Lineage Consumer Initialized.")
    
    yield
    
    # Clean shutdown
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
    return {
        "status": "Aether-Gate is Breathing", 
        "system": "Arch Linux",
        "redis_connected": redis_client.ping()
    }

@app.get("/pending-interventions")
async def get_pending():
    """Fetch 'Dirty' records trapped in the Redis Waiting Room"""
    keys = redis_client.keys("intervention:*")
    
    # Fetch all records and parse them back to JSON for the frontend
    items = []
    for k in keys:
        raw_data = redis_client.get(k)
        if raw_data:
            items.append(json.loads(raw_data))
            
    return {
        "count": len(items), 
        "items": items
    }

@app.post("/intervene/{transaction_id}")
async def submit_intervention(transaction_id: str, corrected_data: dict):
    """
    Manually 'Promotes' a fixed record from Bronze/Silver to Gold logic.
    In a real Lakehouse, this would trigger a write to Apache Iceberg.
    """
    # Remove from Redis once the human (you) has fixed it
    result = redis_client.delete(f"intervention:{transaction_id}")
    
    if result:
        print(f"🛠️ MANUAL FIX APPLIED: TX_{transaction_id}")
        # Logic for writing the 'corrected_data' to your Silver/Gold Iceberg table goes here
        return {"status": "success", "message": f"Transaction {transaction_id} promoted to Gold."}
    
    return {"status": "error", "message": "Transaction not found or already processed."}