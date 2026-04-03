import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from redis import Redis
from .kafka_consumer import start_gatekeeper

# Connect to our Dockerized Redis
redis_client = Redis(host='localhost', port=6379, db=0, decode_responses=True)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # This starts the Kafka listener in the background when the API starts
    task = asyncio.create_task(start_gatekeeper())
    print("🚀 Aether-Gate Lineage Consumer Started...")
    yield
    task.cancel()

app = FastAPI(title="Aether-Gate API", lifespan=lifespan)

@app.get("/")
async def root():
    return {"status": "Aether-Gate is Breathing", "system": "Arch Linux"}

@app.get("/pending-interventions")
async def get_pending():
    # Pull "dirty" records from Redis for the Next.js UI
    keys = redis_client.keys("intervention:*")
    data = [redis_client.get(k) for k in keys]
    return {"count": len(data), "items": data}