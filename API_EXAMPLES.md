# Example API Usage Guide

## User Registration Flow

### 1. Send OTP
```bash
curl -X POST "http://localhost:8000/api/user/register/send-otp" \
  -H "Content-Type: application/json" \
  -d '{"phone_number": "03001234567"}'
```

Response:
```json
{
  "message": "OTP sent successfully",
  "phone_number": "03001234567"
}
```

### 2. Verify OTP
```bash
curl -X POST "http://localhost:8000/api/user/register/verify-otp" \
  -H "Content-Type: application/json" \
  -d '{"phone_number": "03001234567", "otp": "123456"}'
```

Response:
```json
{
  "message": "OTP verified successfully",
  "phone_number": "03001234567"
}
```

### 3. Complete Registration
```bash
curl -X POST "http://localhost:8000/api/user/register/complete" \
  -H "Content-Type: application/json" \
  -d '{
    "phone_number": "03001234567",
    "password": "securePassword123"
  }'
```

Response:
```json
{
  "id": "507f1f77bcf86cd799439011",
  "phone_number": "03001234567",
  "is_active": true,
  "is_verified": true,
  "created_at": "2026-01-28T10:30:00"
}
```

## User Login

```bash
curl -X POST "http://localhost:8000/api/user/login" \
  -H "Content-Type: application/json" \
  -d '{
    "phone_number": "03001234567",
    "password": "securePassword123"
  }'
```

Response:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

## User Logout

```bash
curl -X POST "http://localhost:8000/api/user/logout" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

Response:
```json
{
  "message": "Successfully logged out",
  "detail": "Your session has been terminated. Please login again to access your account."
}
```

**Note**: After logout, the token is blacklisted and cannot be used anymore. User must login again to get a new token.

## Create Service Request

```bash
curl -X POST "http://localhost:8000/api/user/service-request" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -d '{
    "service_type": "plumber",
    "name": "John Doe",
    "address": "House 123, Street 45, Lahore",
    "contact_number": "03001234567",
    "preferred_time": "2026-01-29T14:00:00",
    "issue_description": "Kitchen sink is leaking badly and needs immediate repair"
  }'
```

Response:
```json
{
  "id": "507f1f77bcf86cd799439012",
  "user_id": "507f1f77bcf86cd799439011",
  "service_type": "plumber",
  "name": "John Doe",
  "address": "House 123, Street 45, Lahore",
  "contact_number": "03001234567",
  "preferred_time": "2026-01-29T14:00:00",
  "issue_description": "Kitchen sink is leaking badly and needs immediate repair",
  "status": "pending",
  "admin_response": null,
  "technician_name": null,
  "estimated_arrival_time": null,
  "created_at": "2026-01-28T10:35:00",
  "updated_at": "2026-01-28T10:35:00",
  "completed_at": null
}
```

## Admin Login

```bash
curl -X POST "http://localhost:8000/api/admin/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@serviceapp.com",
    "password": "admin123"
  }'
```

## Admin: View Service Requests

```bash
curl -X GET "http://localhost:8000/api/admin/service-requests?status_filter=pending" \
  -H "Authorization: Bearer ADMIN_TOKEN_HERE"
```

## Admin: Update Service Request

```bash
curl -X PATCH "http://localhost:8000/api/admin/service-request/507f1f77bcf86cd799439012" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ADMIN_TOKEN_HERE" \
  -d '{
    "status": "assigned",
    "admin_response": "We have received your request. A technician will be assigned shortly.",
    "technician_name": "Ahmed Ali",
    "estimated_arrival_time": "2026-01-29T14:30:00"
  }'
```

## Admin Logout

```bash
curl -X POST "http://localhost:8000/api/admin/logout" \
  -H "Authorization: Bearer ADMIN_TOKEN_HERE"
```

Response:
```json
{
  "message": "Admin successfully logged out",
  "detail": "Your admin session has been terminated. Please login again to access the admin panel."
}
```

## Admin: Get Analytics

```bash
curl -X GET "http://localhost:8000/api/admin/analytics" \
  -H "Authorization: Bearer ADMIN_TOKEN_HERE"
```

Response:
```json
{
  "total_requests": 150,
  "pending_requests": 12,
  "completed_requests": 120,
  "cancelled_requests": 18,
  "plumber_requests": 85,
  "electrician_requests": 65,
  "average_completion_time_hours": 4.5,
  "average_rating": 4.3,
  "top_rated_technicians": [
    {
      "technician_name": "Ahmed Ali",
      "average_rating": 4.8,
      "total_ratings": 45
    }
  ]
}
```

## User: Submit Feedback

```bash
curl -X POST "http://localhost:8000/api/user/feedback" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer USER_TOKEN_HERE" \
  -d '{
    "service_request_id": "507f1f77bcf86cd799439012",
    "rating": 5,
    "comment": "Excellent service! The plumber was very professional and fixed the issue quickly."
  }'
```

## Service Types
- `plumber` - For plumbing services
- `electrician` - For electrical services

## Request Status Values
- `pending` - Request submitted, waiting for admin response
- `assigned` - Technician assigned to the request
- `in_progress` - Technician is working on the issue
- `completed` - Service completed
- `cancelled` - Request cancelled
