from motor.motor_asyncio import AsyncIOMotorClient
from config import settings
from typing import Optional
import ssl
import certifi
import os

# Set SSL environment variables for better compatibility
os.environ['PYTHONHTTPSVERIFY'] = '0'

class Database:
    client: Optional[AsyncIOMotorClient] = None
    
    
database = Database()


async def get_database():
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
        # Method 1: Try with tlsAllowInvalidCertificates (most compatible)
        print("🔄 Connecting to MongoDB (allowing invalid certificates)...")
        database.client = AsyncIOMotorClient(
            settings.MONGODB_URL,
            tls=True,
            tlsAllowInvalidCertificates=True,
            tlsInsecure=True,
            **connection_options
        )
        # Test the connection
        await database.client.admin.command('ping')
        print("✅ Connected to MongoDB successfully")
        return
    except Exception as e:
        print(f"⚠️  Method 1 failed: {str(e)[:150]}")
    
    try:
        # Method 2: Try with certifi SSL
        print("🔄 Trying with certifi SSL...")
        database.client = AsyncIOMotorClient(
            settings.MONGODB_URL,
            tlsCAFile=certifi.where(),
            tlsAllowInvalidCertificates=True,
            **connection_options
        )
        await database.client.admin.command('ping')
        print("✅ Connected to MongoDB with certifi")
        return
    except Exception as e:
        print(f"⚠️  Method 2 failed: {str(e)[:150]}")
    
    try:
        # Method 3: Disable all SSL verification
        print("🔄 Trying with disabled SSL verification...")
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        
        # Remove SSL params from connection string and let our context handle it
        clean_url = settings.MONGODB_URL.split('?')[0]
        
        database.client = AsyncIOMotorClient(
            clean_url,
            tls=True,
            tlsAllowInvalidCertificates=True,
            tlsInsecure=True,
            **connection_options
        )
        await database.client.admin.command('ping')
        print("✅ Connected to MongoDB with custom SSL context")
        return
    except Exception as e:
        print(f"❌ All connection attempts failed: {str(e)[:150]}")
        print("⚠️  Database operations will fail - check MongoDB Atlas settings")
        database.client = None


async def close_mongo_connection():
    """Close MongoDB connection"""
    if database.client:
        database.client.close()
        print("Closed MongoDB connection")
