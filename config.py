from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # MongoDB
    MONGODB_URL: str = "mongodb://localhost:27017"
    DATABASE_NAME: str = "service_request_app"
    
    # JWT
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 10080  # 7 days
    
    # Zong SMS API
    ZONG_API_URL: str
    ZONG_LOGIN_ID: str
    ZONG_PASSWORD: str
    ZONG_MASK: str
    
    # Admin
    ADMIN_DEFAULT_EMAIL: str = "admin@serviceapp.com"
    ADMIN_DEFAULT_PASSWORD: str = "admin123"
    
    # OTP
    OTP_EXPIRY_MINUTES: int = 5
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
