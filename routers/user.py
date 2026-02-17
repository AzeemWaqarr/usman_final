from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from datetime import datetime
from typing import List
from bson import ObjectId
from database import get_database
from models import (
    OTPRequest, OTPVerify, UserCreate, UserLogin, UserResponse,
    Token, ServiceRequestCreate, ServiceRequestResponse, ServiceRequestInDB,
    FeedbackCreate, FeedbackResponse, RequestStatus, ServiceType
)
from auth import (
    get_password_hash, verify_password, create_access_token,
    get_current_user
)
from otp_service import generate_otp, store_otp, verify_otp, send_otp_via_zong, send_notification_sms
from models import TokenData, UserRole

router = APIRouter(prefix="/api/user", tags=["User"])
security = HTTPBearer()


@router.post("/register/send-otp")
async def send_registration_otp(request: OTPRequest, db=Depends(get_database)):
    """Send OTP for user registration"""
    # Check if user already exists
    users_collection = db["users"]
    existing_user = await users_collection.find_one({"phone_number": request.phone_number})
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this phone number already exists"
        )
    
    # Generate and send OTP
    otp = generate_otp()
    store_otp(request.phone_number, otp)
    
    success = await send_otp_via_zong(request.phone_number, otp)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send OTP"
        )
    
    return {"message": "OTP sent successfully", "phone_number": request.phone_number}


@router.post("/register/verify-otp")
async def verify_registration_otp(request: OTPVerify):
    """Verify OTP for registration"""
    if not verify_otp(request.phone_number, request.otp):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired OTP"
        )
    
    return {"message": "OTP verified successfully", "phone_number": request.phone_number}


@router.post("/register/complete", response_model=Token)
async def complete_registration(user: UserCreate, db=Depends(get_database)):
    """Complete user registration after OTP verification and return auth token"""
    users_collection = db["users"]
    
    # Check if user already exists
    existing_user = await users_collection.find_one({"phone_number": user.phone_number})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already exists"
        )
    
    # Create user
    user_dict = {
        "phone_number": user.phone_number,
        "hashed_password": get_password_hash(user.password),
        "is_active": True,
        "is_verified": True,
        "created_at": datetime.utcnow()
    }
    
    result = await users_collection.insert_one(user_dict)
    user_id = str(result.inserted_id)
    
    # Create access token for immediate login
    access_token = create_access_token(
        data={"sub": user_id, "role": UserRole.USER.value}
    )
    
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/login", response_model=Token)
async def login(user: UserLogin, db=Depends(get_database)):
    """User login"""
    users_collection = db["users"]
    
    # Find user
    db_user = await users_collection.find_one({"phone_number": user.phone_number})
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect phone number or password"
        )
    
    # Verify password
    if not verify_password(user.password, db_user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect phone number or password"
        )
    
    # Create access token
    access_token = create_access_token(
        data={"sub": str(db_user["_id"]), "role": UserRole.USER.value}
    )
    
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/logout")
async def logout(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    current_user: TokenData = Depends(get_current_user)
):
    """Logout user by blacklisting their token"""
    try:
        from otp_service import blacklist_token
        
        # Get the token from the request
        token = credentials.credentials
        
        # Add token to blacklist
        blacklist_token(token)
        
        return {
            "message": "Successfully logged out",
            "detail": "Your session has been terminated. Please login again to access your account."
        }
    except Exception as e:
        print(f"Logout error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Logout failed: {str(e)}"
        )


@router.post("/service-request", response_model=ServiceRequestResponse)
async def create_service_request(
    request: ServiceRequestCreate,
    current_user: TokenData = Depends(get_current_user),
    db=Depends(get_database)
):
    """Create a new service request"""
    requests_collection = db["service_requests"]
    
    # Initialize hourly booking fields
    hours_required = request.hours_required
    hourly_rate = None
    total_cost = None
    
    # For Helper service, set hourly rate to 600 PKR and calculate total cost
    if request.service_type == ServiceType.HELPER and hours_required:
        hourly_rate = 600.0
        total_cost = hours_required * hourly_rate
    
    request_dict = {
        "user_id": current_user.user_id,
        "service_type": request.service_type.value,
        "name": request.name,
        "address": request.address,
        "contact_number": request.contact_number,
        "preferred_time": request.preferred_time,
        "issue_description": request.issue_description,
        "hours_required": hours_required,
        "hourly_rate": hourly_rate,
        "total_cost": total_cost,
        "status": RequestStatus.PENDING.value,
        "admin_response": None,
        "technician_name": None,
        "technician_phone": None,
        "estimated_arrival_time": None,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
        "completed_at": None
    }
    
    result = await requests_collection.insert_one(request_dict)
    request_dict["_id"] = str(result.inserted_id)
    
    return ServiceRequestResponse(
        id=request_dict["_id"],
        user_id=request_dict["user_id"],
        service_type=request_dict["service_type"],
        name=request_dict["name"],
        address=request_dict["address"],
        contact_number=request_dict["contact_number"],
        preferred_time=request_dict["preferred_time"],
        issue_description=request_dict["issue_description"],
        hours_required=request_dict.get("hours_required"),
        hourly_rate=request_dict.get("hourly_rate"),
        total_cost=request_dict.get("total_cost"),
        status=request_dict["status"],
        admin_response=request_dict["admin_response"],
        technician_name=request_dict["technician_name"],        technician_phone=request_dict.get("technician_phone"),        estimated_arrival_time=request_dict["estimated_arrival_time"],
        created_at=request_dict["created_at"],
        updated_at=request_dict["updated_at"],
        completed_at=request_dict["completed_at"]
    )


@router.get("/service-requests", response_model=List[ServiceRequestResponse])
async def get_user_service_requests(
    current_user: TokenData = Depends(get_current_user),
    db=Depends(get_database)
):
    """Get all service requests for the current user"""
    requests_collection = db["service_requests"]
    
    requests = await requests_collection.find(
        {"user_id": current_user.user_id}
    ).sort("created_at", -1).to_list(length=100)
    
    return [
        ServiceRequestResponse(
            id=str(req["_id"]),
            user_id=req["user_id"],
            service_type=req["service_type"],
            name=req["name"],
            address=req["address"],
            contact_number=req["contact_number"],
            preferred_time=req["preferred_time"],
            issue_description=req["issue_description"],
            hours_required=req.get("hours_required"),
            hourly_rate=req.get("hourly_rate"),
            total_cost=req.get("total_cost"),
            status=req["status"],
            admin_response=req.get("admin_response"),
            technician_name=req.get("technician_name"),
            technician_phone=req.get("technician_phone"),
            estimated_arrival_time=req.get("estimated_arrival_time"),
            created_at=req["created_at"],
            updated_at=req["updated_at"],
            completed_at=req.get("completed_at")
        )
        for req in requests
    ]


@router.get("/service-request/{request_id}", response_model=ServiceRequestResponse)
async def get_service_request(
    request_id: str,
    current_user: TokenData = Depends(get_current_user),
    db=Depends(get_database)
):
    """Get a specific service request"""
    requests_collection = db["service_requests"]
    
    try:
        request = await requests_collection.find_one({
            "_id": ObjectId(request_id),
            "user_id": current_user.user_id
        })
    except:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid request ID"
        )
    
    if not request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service request not found"
        )
    
    return ServiceRequestResponse(
        id=str(request["_id"]),
        user_id=request["user_id"],
        service_type=request["service_type"],
        name=request["name"],
        address=request["address"],
        contact_number=request["contact_number"],
        preferred_time=request["preferred_time"],
        issue_description=request["issue_description"],
        hours_required=request.get("hours_required"),
        hourly_rate=request.get("hourly_rate"),
        total_cost=request.get("total_cost"),
        status=request["status"],
        admin_response=request.get("admin_response"),
        technician_name=request.get("technician_name"),
        technician_phone=request.get("technician_phone"),
        estimated_arrival_time=request.get("estimated_arrival_time"),
        created_at=request["created_at"],
        updated_at=request["updated_at"],
        completed_at=request.get("completed_at")
    )


@router.post("/feedback", response_model=FeedbackResponse)
async def submit_feedback(
    feedback: FeedbackCreate,
    current_user: TokenData = Depends(get_current_user),
    db=Depends(get_database)
):
    """Submit feedback for a completed service request"""
    requests_collection = db["service_requests"]
    feedback_collection = db["feedback"]
    
    # Verify service request exists and belongs to user
    try:
        service_request = await requests_collection.find_one({
            "_id": ObjectId(feedback.service_request_id),
            "user_id": current_user.user_id
        })
    except:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid service request ID"
        )
    
    if not service_request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service request not found"
        )
    
    if service_request["status"] != RequestStatus.COMPLETED.value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Can only submit feedback for completed requests"
        )
    
    # Check if feedback already exists
    existing_feedback = await feedback_collection.find_one({
        "service_request_id": feedback.service_request_id
    })
    
    if existing_feedback:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Feedback already submitted for this request"
        )
    
    # Create feedback
    feedback_dict = {
        "service_request_id": feedback.service_request_id,
        "user_id": current_user.user_id,
        "technician_name": service_request.get("technician_name", "Unknown"),
        "service_type": service_request["service_type"],
        "rating": feedback.rating,
        "comment": feedback.comment,
        "created_at": datetime.utcnow()
    }
    
    result = await feedback_collection.insert_one(feedback_dict)
    feedback_dict["_id"] = str(result.inserted_id)
    
    return FeedbackResponse(
        id=feedback_dict["_id"],
        service_request_id=feedback_dict["service_request_id"],
        user_id=feedback_dict["user_id"],
        technician_name=feedback_dict["technician_name"],
        service_type=feedback_dict["service_type"],
        rating=feedback_dict["rating"],
        comment=feedback_dict["comment"],
        created_at=feedback_dict["created_at"]
    )


@router.get("/my-feedback", response_model=List[FeedbackResponse])
async def get_user_feedback(
    current_user: TokenData = Depends(get_current_user),
    db=Depends(get_database)
):
    """Get all feedback submitted by the current user"""
    feedback_collection = db["feedback"]
    
    feedback_list = await feedback_collection.find(
        {"user_id": current_user.user_id}
    ).sort("created_at", -1).to_list(length=100)
    
    return [
        FeedbackResponse(
            id=str(fb["_id"]),
            service_request_id=fb["service_request_id"],
            user_id=fb["user_id"],
            technician_name=fb["technician_name"],
            service_type=fb["service_type"],
            rating=fb["rating"],
            comment=fb.get("comment"),
            created_at=fb["created_at"]
        )
        for fb in feedback_list
    ]
