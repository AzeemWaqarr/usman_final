from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from datetime import datetime
from typing import List, Optional
from bson import ObjectId
from database import get_database
from models import (
    AdminCreate, AdminLogin, AdminResponse, Token,
    ServiceRequestResponse, ServiceRequestUpdate, RequestStatus,
    FeedbackResponse, AnalyticsResponse, TechnicianPerformance,
    ServiceType
)
from auth import (
    get_password_hash, verify_password, create_access_token,
    get_current_admin
)
from otp_service import send_notification_sms
from models import TokenData, UserRole

router = APIRouter(prefix="/api/admin", tags=["Admin"])
security = HTTPBearer()


@router.post("/register", response_model=AdminResponse)
async def create_admin(admin: AdminCreate, db=Depends(get_database)):
    """Create a new admin (should be protected in production)"""
    admins_collection = db["admins"]
    
    # Check if admin exists
    existing_admin = await admins_collection.find_one({"email": admin.email})
    if existing_admin:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Admin with this email already exists"
        )
    
    # Create admin
    admin_dict = {
        "email": admin.email,
        "hashed_password": get_password_hash(admin.password),
        "full_name": admin.full_name,
        "role": UserRole.ADMIN.value,
        "is_active": True,
        "created_at": datetime.utcnow()
    }
    
    result = await admins_collection.insert_one(admin_dict)
    admin_dict["_id"] = str(result.inserted_id)
    
    return AdminResponse(
        id=admin_dict["_id"],
        email=admin_dict["email"],
        full_name=admin_dict["full_name"],
        role=admin_dict["role"],
        is_active=admin_dict["is_active"],
        created_at=admin_dict["created_at"]
    )


@router.post("/login", response_model=Token)
async def admin_login(admin: AdminLogin, db=Depends(get_database)):
    """Admin login"""
    admins_collection = db["admins"]
    
    # Find admin
    db_admin = await admins_collection.find_one({"email": admin.email})
    if not db_admin:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    # Verify password
    if not verify_password(admin.password, db_admin["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    # Create access token
    access_token = create_access_token(
        data={"sub": str(db_admin["_id"]), "role": UserRole.ADMIN.value}
    )
    
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/logout")
async def admin_logout(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    current_admin: TokenData = Depends(get_current_admin)
):
    """Logout admin by blacklisting their token"""
    from otp_service import blacklist_token
    
    # Get the token from the request
    token = credentials.credentials
    
    # Add token to blacklist
    blacklist_token(token)
    
    return {
        "message": "Admin successfully logged out",
        "detail": "Your admin session has been terminated. Please login again to access the admin panel."
    }


@router.get("/service-requests", response_model=List[ServiceRequestResponse])
async def get_all_service_requests(
    status_filter: Optional[RequestStatus] = None,
    service_type_filter: Optional[ServiceType] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_admin: TokenData = Depends(get_current_admin),
    db=Depends(get_database)
):
    """Get all service requests with optional filters"""
    requests_collection = db["service_requests"]
    
    # Build query
    query = {}
    if status_filter:
        query["status"] = status_filter.value
    if service_type_filter:
        query["service_type"] = service_type_filter.value
    
    # Get requests
    requests = await requests_collection.find(query).sort(
        "created_at", -1
    ).skip(skip).limit(limit).to_list(length=limit)
    
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
async def get_service_request_detail(
    request_id: str,
    current_admin: TokenData = Depends(get_current_admin),
    db=Depends(get_database)
):
    """Get detailed information about a specific service request"""
    requests_collection = db["service_requests"]
    
    try:
        request = await requests_collection.find_one({"_id": ObjectId(request_id)})
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


@router.patch("/service-request/{request_id}", response_model=ServiceRequestResponse)
async def update_service_request(
    request_id: str,
    update_data: ServiceRequestUpdate,
    current_admin: TokenData = Depends(get_current_admin),
    db=Depends(get_database)
):
    """Update a service request (admin response, status, technician assignment)"""
    requests_collection = db["service_requests"]
    users_collection = db["users"]
    
    try:
        request = await requests_collection.find_one({"_id": ObjectId(request_id)})
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
    
    # Prepare update data
    update_dict = {"updated_at": datetime.utcnow()}
    
    if update_data.status:
        update_dict["status"] = update_data.status.value
        if update_data.status == RequestStatus.COMPLETED:
            update_dict["completed_at"] = datetime.utcnow()
    
    if update_data.admin_response:
        update_dict["admin_response"] = update_data.admin_response
    
    if update_data.technician_name:
        update_dict["technician_name"] = update_data.technician_name
    
    if update_data.technician_phone:
        update_dict["technician_phone"] = update_data.technician_phone
    
    if update_data.estimated_arrival_time:
        update_dict["estimated_arrival_time"] = update_data.estimated_arrival_time
    
    # Update request
    await requests_collection.update_one(
        {"_id": ObjectId(request_id)},
        {"$set": update_dict}
    )
    
    # Send notification to user
    user = await users_collection.find_one({"_id": ObjectId(request["user_id"])})
    if user and update_data.admin_response:
        message = f"Update on your {request['service_type']} request: {update_data.admin_response}"
        await send_notification_sms(user["phone_number"], message)
    
    # Send notification if technician is on the way
    if update_data.estimated_arrival_time and user:
        # Handle both string and datetime types for estimated_arrival_time
        eta_str = update_data.estimated_arrival_time
        if isinstance(eta_str, datetime):
            eta_str = eta_str.strftime('%I:%M %p')
        eta_message = f"Your technician {update_data.technician_name or 'our technician'} is on the way! Expected arrival: {eta_str}"
        await send_notification_sms(user["phone_number"], eta_message)
    
    # Get updated request
    updated_request = await requests_collection.find_one({"_id": ObjectId(request_id)})
    
    return ServiceRequestResponse(
        id=str(updated_request["_id"]),
        user_id=updated_request["user_id"],
        service_type=updated_request["service_type"],
        name=updated_request["name"],
        address=updated_request["address"],
        contact_number=updated_request["contact_number"],
        preferred_time=updated_request["preferred_time"],
        issue_description=updated_request["issue_description"],
        hours_required=updated_request.get("hours_required"),
        hourly_rate=updated_request.get("hourly_rate"),
        total_cost=updated_request.get("total_cost"),
        status=updated_request["status"],
        admin_response=updated_request.get("admin_response"),
        technician_name=updated_request.get("technician_name"),
        technician_phone=updated_request.get("technician_phone"),
        estimated_arrival_time=updated_request.get("estimated_arrival_time"),
        created_at=updated_request["created_at"],
        updated_at=updated_request["updated_at"],
        completed_at=updated_request.get("completed_at")
    )


@router.get("/analytics", response_model=AnalyticsResponse)
async def get_analytics(
    current_admin: TokenData = Depends(get_current_admin),
    db=Depends(get_database)
):
    """Get analytics dashboard data"""
    requests_collection = db["service_requests"]
    feedback_collection = db["feedback"]
    
    # Get all requests
    all_requests = await requests_collection.find({}).to_list(length=None)
    
    # Calculate basic metrics
    total_requests = len(all_requests)
    pending_requests = len([r for r in all_requests if r["status"] == RequestStatus.PENDING.value])
    completed_requests = len([r for r in all_requests if r["status"] == RequestStatus.COMPLETED.value])
    cancelled_requests = len([r for r in all_requests if r["status"] == RequestStatus.CANCELLED.value])
    plumber_requests = len([r for r in all_requests if r["service_type"] == ServiceType.PLUMBER.value])
    electrician_requests = len([r for r in all_requests if r["service_type"] == ServiceType.ELECTRICIAN.value])
    driver_requests = len([r for r in all_requests if r["service_type"] == ServiceType.DRIVER.value])
    helper_requests = len([r for r in all_requests if r["service_type"] == ServiceType.HELPER.value])
    
    # Calculate average completion time
    completed_with_times = [
        r for r in all_requests 
        if r["status"] == RequestStatus.COMPLETED.value and r.get("completed_at")
    ]
    
    average_completion_time = None
    if completed_with_times:
        total_time = sum([
            (r["completed_at"] - r["created_at"]).total_seconds() / 3600
            for r in completed_with_times
        ])
        average_completion_time = total_time / len(completed_with_times)
    
    # Get feedback data
    all_feedback = await feedback_collection.find({}).to_list(length=None)
    
    average_rating = None
    if all_feedback:
        total_rating = sum([f["rating"] for f in all_feedback])
        average_rating = total_rating / len(all_feedback)
    
    # Get top rated technicians
    technician_ratings = {}
    for feedback in all_feedback:
        tech_name = feedback.get("technician_name", "Unknown")
        if tech_name not in technician_ratings:
            technician_ratings[tech_name] = {"ratings": [], "count": 0}
        technician_ratings[tech_name]["ratings"].append(feedback["rating"])
        technician_ratings[tech_name]["count"] += 1
    
    top_rated = []
    for tech_name, data in technician_ratings.items():
        avg_rating = sum(data["ratings"]) / len(data["ratings"])
        top_rated.append({
            "technician_name": tech_name,
            "average_rating": round(avg_rating, 2),
            "total_ratings": data["count"]
        })
    
    top_rated = sorted(top_rated, key=lambda x: x["average_rating"], reverse=True)[:10]
    
    return AnalyticsResponse(
        total_requests=total_requests,
        pending_requests=pending_requests,
        completed_requests=completed_requests,
        cancelled_requests=cancelled_requests,
        plumber_requests=plumber_requests,
        electrician_requests=electrician_requests,
        driver_requests=driver_requests,
        helper_requests=helper_requests,
        average_completion_time_hours=round(average_completion_time, 2) if average_completion_time else None,
        average_rating=round(average_rating, 2) if average_rating else None,
        top_rated_technicians=top_rated
    )


@router.get("/technician-performance", response_model=List[TechnicianPerformance])
async def get_technician_performance(
    current_admin: TokenData = Depends(get_current_admin),
    db=Depends(get_database)
):
    """Get performance metrics for all technicians"""
    requests_collection = db["service_requests"]
    feedback_collection = db["feedback"]
    
    # Get all requests with assigned technicians
    all_requests = await requests_collection.find({
        "technician_name": {"$exists": True, "$ne": None}
    }).to_list(length=None)
    
    # Get all feedback
    all_feedback = await feedback_collection.find({}).to_list(length=None)
    
    # Build technician performance data
    technician_data = {}
    
    for request in all_requests:
        tech_name = request.get("technician_name")
        if tech_name and tech_name not in technician_data:
            technician_data[tech_name] = {
                "total_jobs": 0,
                "completed_jobs": 0,
                "ratings": []
            }
        
        if tech_name:
            technician_data[tech_name]["total_jobs"] += 1
            if request["status"] == RequestStatus.COMPLETED.value:
                technician_data[tech_name]["completed_jobs"] += 1
    
    for feedback in all_feedback:
        tech_name = feedback.get("technician_name")
        if tech_name and tech_name in technician_data:
            technician_data[tech_name]["ratings"].append(feedback["rating"])
    
    # Create performance list
    performance_list = []
    for tech_name, data in technician_data.items():
        avg_rating = sum(data["ratings"]) / len(data["ratings"]) if data["ratings"] else 0
        performance_list.append(
            TechnicianPerformance(
                technician_name=tech_name,
                total_jobs=data["total_jobs"],
                completed_jobs=data["completed_jobs"],
                average_rating=round(avg_rating, 2),
                total_ratings=len(data["ratings"])
            )
        )
    
    return sorted(performance_list, key=lambda x: x.average_rating, reverse=True)


@router.get("/feedback", response_model=List[FeedbackResponse])
async def get_all_feedback(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_admin: TokenData = Depends(get_current_admin),
    db=Depends(get_database)
):
    """Get all feedback submissions"""
    feedback_collection = db["feedback"]
    
    feedback_list = await feedback_collection.find({}).sort(
        "created_at", -1
    ).skip(skip).limit(limit).to_list(length=limit)
    
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
