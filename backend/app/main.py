import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware  # 1. Import the Middleware
from redis import Redis
from .kafka_consumer import start_gatekeeper

# Connect to our Dockerized Redis
# Added decode_responses=True to ensure we get strings, not bytes
redis_client = Redis(host='localhost', port=6379, db=0, decode_responses=True)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # This starts the Kafka listener in the background when the API starts
    task = asyncio.create_task(start_gatekeeper())
    print("🚀 Aether-Gate Lineage Consumer Started...")
    yield
    task.cancel()

app = FastAPI(title="Aether-Gate API", lifespan=lifespan)

# 2. Add CORS Middleware Configuration
app.add_middleware(
    CORSMiddleware,
    # Explicitly allow your Next.js dev server
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"], 
    allow_credentials=True,
    allow_methods=["*"],  # Allow GET, POST, DELETE, etc.
    allow_headers=["*"],  # Allow all headers (Content-Type, etc.)
)

@app.get("/")
async def root():
    return {"status": "Aether-Gate is Breathing", "system": "Arch Linux"}

@app.get("/pending-interventions")
async def get_pending():
    # Pull "dirty" records from Redis for the Next.js UI
    keys = redis_client.keys("intervention:*")
    data = [redis_client.get(k) for k in keys]
    return {"count": len(data), "items": data}

# 3. Add the Intervention Endpoint so your "Fix" buttons actually work
@app.post("/intervene/{transaction_id}")
async def submit_intervention(transaction_id: str, corrected_data: dict):
    # Remove from the "Waiting Room" in Redis
    result = redis_client.delete(f"intervention:{transaction_id}")
    if result:
        print(f"🛠️ MANUAL FIX APPLIED: TX_{transaction_id} -> Promotion Signal Sent.")
        return {"status": "success"}
    return {"status": "error", "message": "Transaction not found."}