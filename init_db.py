import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime
from auth import get_password_hash
from config import settings

async def init_database():
    print("🔄 Connecting to MongoDB Atlas...")
    
    try:
        client = AsyncIOMotorClient(settings.MONGODB_URL, serverSelectionTimeoutMS=5000)
        
        # Test connection
        await client.admin.command('ping')
        print("✅ Connected to MongoDB Atlas successfully!")
        
        db = client[settings.DATABASE_NAME]
        
        # Create collections with indexes
        print("🔄 Creating collections and indexes...")
        
        # Users collection
        users_collection = db["users"]
        await users_collection.create_index("phone_number", unique=True)
        print("✅ Users collection created")
        
        # Admins collection
        admins_collection = db["admins"]
        await admins_collection.create_index("email", unique=True)
        
        # Check if admin exists
        existing_admin = await admins_collection.find_one({
            "email": settings.ADMIN_DEFAULT_EMAIL
        })
        
        if not existing_admin:
            admin_dict = {
                "email": settings.ADMIN_DEFAULT_EMAIL,
                "hashed_password": get_password_hash(settings.ADMIN_DEFAULT_PASSWORD),
                "full_name": "System Administrator",
                "role": "admin",
                "is_active": True,
                "created_at": datetime.utcnow()
            }
            
            await admins_collection.insert_one(admin_dict)
            print(f"✅ Admin user created: {settings.ADMIN_DEFAULT_EMAIL}")
        else:
            print(f"ℹ️  Admin user already exists: {settings.ADMIN_DEFAULT_EMAIL}")
        
        # Service requests collection
        service_requests_collection = db["service_requests"]
        await service_requests_collection.create_index("user_id")
        await service_requests_collection.create_index("status")
        await service_requests_collection.create_index("created_at")
        print("✅ Service requests collection created")
        
        # Feedback collection
        feedback_collection = db["feedback"]
        await feedback_collection.create_index("service_request_id", unique=True)
        await feedback_collection.create_index("user_id")
        print("✅ Feedback collection created")
        
        # OTPs collection (for phone verification)
        otp_collection = db["otps"]
        await otp_collection.create_index("phone_number")
        await otp_collection.create_index("created_at", expireAfterSeconds=300)  # Auto-delete after 5 minutes
        print("✅ OTP collection created")
        
        print("\n🎉 Database initialization complete!")
        print(f"📊 Database: {settings.DATABASE_NAME}")
        print(f"🌍 Region: Mumbai, India (ap-south-1)")
        print(f"👤 Admin Email: {settings.ADMIN_DEFAULT_EMAIL}")
        print(f"🔑 Admin Password: {settings.ADMIN_DEFAULT_PASSWORD}")
        
        client.close()
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        print("\n🔍 Troubleshooting:")
        print("1. Check if MONGODB_URL is correct in .env file")
        print("2. Ensure you replaced <password> with your actual password")
        print("3. Verify Network Access allows your IP (0.0.0.0/0)")
        print("4. Check if cluster is fully deployed (wait 3-5 minutes)")

if __name__ == "__main__":
    asyncio.run(init_database())