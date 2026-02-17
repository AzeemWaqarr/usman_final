from motor.motor_asyncio import AsyncIOMotorClient
from config import settings
from typing import Optional
from fastapi import HTTPException, status
import ssl
import certifi
import os

# Set SSL environment variables for better compatibility
os.environ['PYTHONHTTPSVERIFY'] = '0'

class Database:
    client: Optional[AsyncIOMotorClient] = None
    
    
database = Database()


async def get_database():
    """Get database instance, raise error if not connected"""
    if database.client is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database connection not available. Please try again later."
        )
    return database.client[settings.DATABASE_NAME]


async def connect_to_mongo():
    """Connect to MongoDB with SSL handling for Python 3.11+"""
    
    # MongoDB connection options
    connection_options = {
        "serverSelectionTimeoutMS": 15000,
        "connectTimeoutMS": 15000,
        "socketTimeoutMS": 15000,
        "retryWrites": True,
        "w": "majority",
        "maxPoolSize": 10,
        "minPoolSize": 1,
    }
    
    try:
        # Method 1: Try with tlsAllowInvalidCertificates only
        print("🔄 Connecting to MongoDB (method 1: tlsAllowInvalidCertificates)...")
        database.client = AsyncIOMotorClient(
            settings.MONGODB_URL,
            tls=True,
            tlsAllowInvalidCertificates=True,
            **connection_options
        )
        # Test the connection
        await database.client.admin.command('ping')
        print("✅ Connected to MongoDB successfully!")
        return
    except Exception as e:
        print(f"⚠️  Method 1 failed: {str(e)[:150]}")
        database.client = None
    
    try:
        # Method 2: Try with certifi CA file
        print("🔄 Connecting to MongoDB (method 2: certifi CA file)...")
        database.client = AsyncIOMotorClient(
            settings.MONGODB_URL,
            tlsCAFile=certifi.where(),
            **connection_options
        )
        await database.client.admin.command('ping')
        print("✅ Connected to MongoDB with certifi!")
        return
    except Exception as e:
        print(f"⚠️  Method 2 failed: {str(e)[:150]}")
        database.client = None
    
    try:
        # Method 3: Try with no TLS options (let pymongo handle it)
        print("🔄 Connecting to MongoDB (method 3: default SSL)...")
        database.client = AsyncIOMotorClient(
            settings.MONGODB_URL,
            **connection_options
        )
        await database.client.admin.command('ping')
        print("✅ Connected to MongoDB with default SSL!")
        return
    except Exception as e:
        print(f"⚠️  Method 3 failed: {str(e)[:150]}")
        database.client = None
    
    print("❌ All MongoDB connection attempts failed")
    print("⚠️  Application will return 503 errors for database operations")
    print("💡 Check: 1) MongoDB Atlas IP whitelist, 2) Connection string, 3) Network access")


async def close_mongo_connection():
    """Close MongoDB connection"""
    if database.client:
        database.client.close()
        print("Closed MongoDB connection")
