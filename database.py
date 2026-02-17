from motor.motor_asyncio import AsyncIOMotorClient
from config import settings
from typing import Optional
import ssl
import certifi

class Database:
    client: Optional[AsyncIOMotorClient] = None
    
    
database = Database()


async def get_database():
    return database.client[settings.DATABASE_NAME]


async def connect_to_mongo():
    """Connect to MongoDB"""
    # Fix SSL issues with Python 3.11+
    try:
        database.client = AsyncIOMotorClient(
            settings.MONGODB_URL,
            tlsCAFile=certifi.where(),
            serverSelectionTimeoutMS=5000
        )
        print("✅ Connected to MongoDB")
    except Exception as e:
        print(f"⚠️  MongoDB connection error: {e}")
        print("🔄 Trying without certificate verification...")
        # Fallback: use without cert verification
        try:
            database.client = AsyncIOMotorClient(
                settings.MONGODB_URL,
                tlsAllowInvalidCertificates=True,
                serverSelectionTimeoutMS=5000
            )
            print("✅ Connected to MongoDB (without cert verification)")
        except Exception as e2:
            print(f"❌ MongoDB connection failed: {e2}")
            print("⚠️  Starting without MongoDB connection - database operations will fail")
            # Set to None to allow app to start
            database.client = None


async def close_mongo_connection():
    """Close MongoDB connection"""
    if database.client:
        database.client.close()
        print("Closed MongoDB connection")
