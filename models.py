from pydantic import BaseModel, Field, validator
from typing import Optional, List, Union
from datetime import datetime
from enum import Enum


class ServiceType(str, Enum):
    PLUMBER = "plumber"
    ELECTRICIAN = "electrician"
    DRIVER = "driver"
    HELPER = "helper"


class RequestStatus(str, Enum):
    PENDING = "pending"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class UserRole(str, Enum):
    USER = "user"
    ADMIN = "admin"


# User Models
class UserBase(BaseModel):
    phone_number: str = Field(..., min_length=11, max_length=15)
    
    @validator('phone_number')
    def validate_phone(cls, v):
        if not v.startswith('+92') and not v.startswith('03'):
            raise ValueError('Phone number must be a valid Pakistani number')
        return v


class UserCreate(UserBase):
    password: str = Field(..., min_length=6)


class UserLogin(BaseModel):
    phone_number: str = Field(..., alias="phoneNumber")
    password: str
    
    class Config:
        populate_by_name = True


class OTPRequest(BaseModel):
    phone_number: str


class OTPVerify(BaseModel):
    phone_number: str
    otp: str


class UserInDB(UserBase):
    id: str = Field(alias="_id")
    hashed_password: str
    is_active: bool = True
    is_verified: bool = False
    created_at: datetime
    
    class Config:
        populate_by_name = True


class UserResponse(BaseModel):
    id: str
    phone_number: str
    is_active: bool
    is_verified: bool
    created_at: datetime


# Service Request Models
class ServiceRequestCreate(BaseModel):
    service_type: ServiceType
    name: str = Field(..., min_length=1, max_length=100)
    address: str = Field(..., min_length=1, max_length=500)
    contact_number: str = Field(..., min_length=10, max_length=15)
    preferred_time: datetime
    issue_description: str = Field(..., min_length=1, max_length=1000)
    hours_required: Optional[int] = Field(None, ge=1, le=24, description="Hours required for driver/helper (required for these services)")


class ServiceRequestUpdate(BaseModel):
    status: Optional[RequestStatus] = None
    admin_response: Optional[str] = None
    technician_name: Optional[str] = None
    technician_phone: Optional[str] = None
    estimated_arrival_time: Optional[Union[str, datetime]] = None


class ServiceRequestInDB(BaseModel):
    id: str = Field(alias="_id")
    user_id: str
    service_type: ServiceType
    name: str
    address: str
    contact_number: str
    preferred_time: datetime
    issue_description: str
    hours_required: Optional[int] = None
    hourly_rate: Optional[float] = None
    total_cost: Optional[float] = None
    status: RequestStatus = RequestStatus.PENDING
    admin_response: Optional[str] = None
    technician_name: Optional[str] = None
    technician_phone: Optional[str] = None
    estimated_arrival_time: Optional[Union[str, datetime]] = None
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None
    
    class Config:
        populate_by_name = True


class ServiceRequestResponse(BaseModel):
    id: str
    user_id: str
    service_type: ServiceType
    name: str
    address: str
    contact_number: str
    preferred_time: datetime
    issue_description: str
    hours_required: Optional[int] = None
    hourly_rate: Optional[float] = None
    total_cost: Optional[float] = None
    status: RequestStatus
    admin_response: Optional[str] = None
    technician_name: Optional[str] = None
    technician_phone: Optional[str] = None
    estimated_arrival_time: Optional[Union[str, datetime]] = None
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None


# Admin Models
class AdminCreate(BaseModel):
    email: str
    password: str = Field(..., min_length=6)
    full_name: str


class AdminLogin(BaseModel):
    email: str
    password: str


class AdminInDB(BaseModel):
    id: str = Field(alias="_id")
    email: str
    hashed_password: str
    full_name: str
    role: UserRole = UserRole.ADMIN
    is_active: bool = True
    created_at: datetime
    
    class Config:
        populate_by_name = True


class AdminResponse(BaseModel):
    id: str
    email: str
    full_name: str
    role: UserRole
    is_active: bool
    created_at: datetime


# Feedback Models
class FeedbackCreate(BaseModel):
    service_request_id: str
    rating: int = Field(..., ge=1, le=5)
    comment: Optional[str] = Field(None, max_length=500)


class FeedbackInDB(BaseModel):
    id: str = Field(alias="_id")
    service_request_id: str
    user_id: str
    technician_name: str
    service_type: ServiceType
    rating: int
    comment: Optional[str] = None
    created_at: datetime
    
    class Config:
        populate_by_name = True


class FeedbackResponse(BaseModel):
    id: str
    service_request_id: str
    user_id: str
    technician_name: Optional[str] = None
    service_type: ServiceType
    rating: int
    comment: Optional[str] = None
    created_at: datetime


# Analytics Models
class AnalyticsResponse(BaseModel):
    total_requests: int
    pending_requests: int
    completed_requests: int
    cancelled_requests: int
    plumber_requests: int
    electrician_requests: int
    driver_requests: int
    helper_requests: int
    average_completion_time_hours: Optional[float] = None
    average_rating: Optional[float] = None
    top_rated_technicians: List[dict] = []


class TechnicianPerformance(BaseModel):
    technician_name: str
    total_jobs: int
    completed_jobs: int
    average_rating: float
    total_ratings: int


# Token Models
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    
    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer"
            }
        }


class TokenData(BaseModel):
    user_id: Optional[str] = None
    role: Optional[str] = None
