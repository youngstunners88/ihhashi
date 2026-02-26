from motor.motor_asyncio import AsyncIOMotorClient
from app.config import settings

client: AsyncIOMotorClient = None
database = None

async def connect_db():
    global client, database
    client = AsyncIOMotorClient(settings.mongodb_url)
    database = client[settings.db_name]

async def close_db():
    global client
    if client:
        client.close()

def get_collection(name: str):
    return database[name]
