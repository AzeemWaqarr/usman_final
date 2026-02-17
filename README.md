# Service Request App Backend

A FastAPI-based backend for a service request application that connects users with plumbers and electricians.

## Features

### User Features
- Phone number registration with OTP verification (Zong SMS integration)
- Password-based authentication with JWT tokens
- Request plumber or electrician services
- Submit service requests with details (name, address, contact, time, issue)
- View request status and history
- Receive SMS notifications for request updates
- Submit feedback and ratings for completed services

### Admin Features
- Admin authentication system
- View all service requests with filters (status, service type)
- Respond to service requests
- Assign technicians to requests
- Update request status (pending, assigned, in_progress, completed, cancelled)
- Set estimated arrival times for technicians
- View comprehensive analytics dashboard
- Track technician performance
- View all user feedback

### Analytics Dashboard
- Total requests count
- Pending, completed, and cancelled requests
- Service type breakdown (plumber vs electrician)
- Average completion time
- Average rating across all services
- Top-rated technicians
- Detailed technician performance metrics

## Tech Stack

- **Framework**: FastAPI
- **Database**: MongoDB (Motor async driver)
- **Authentication**: JWT tokens with bcrypt password hashing
- **SMS Service**: Zong SMS API integration
- **Validation**: Pydantic models

## Project Structure

```
app_updated/
├── main.py                 # FastAPI application entry point
├── config.py              # Configuration and environment variables
├── database.py            # MongoDB connection management
├── models.py              # Pydantic models and schemas
├── auth.py                # Authentication utilities (JWT, password hashing)
├── otp_service.py         # OTP generation and SMS sending
├── routes/
│   ├── __init__.py
│   ├── user.py            # User endpoints
│   └── admin.py           # Admin endpoints
├── requirements.txt       # Python dependencies
└── .env.example          # Example environment variables
```

## Installation

1. Clone the repository and navigate to the project directory

2. Create a virtual environment:
```bash
python -m venv venv
```

3. Activate the virtual environment:
```bash
# Windows
.\venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

4. Install dependencies:
```bash
pip install -r requirements.txt
```

5. Copy `.env.example` to `.env` and configure your environment variables:
```bash
cp .env.example .env
```

6. Update the `.env` file with your actual values:
   - MongoDB connection string
   - JWT secret key
   - Zong SMS API credentials

## Running the Application

### Development Mode
```bash
python main.py
```

Or using uvicorn directly:
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

### API Documentation

Once the server is running, access:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## API Endpoints

### User Endpoints

#### Authentication
- `POST /api/user/register/send-otp` - Send OTP for registration
- `POST /api/user/register/verify-otp` - Verify OTP
- `POST /api/user/register/complete` - Complete registration with password
- `POST /api/user/login` - User login

#### Service Requests
- `POST /api/user/service-request` - Create a service request
- `GET /api/user/service-requests` - Get all user's service requests
- `GET /api/user/service-request/{request_id}` - Get specific request details

#### Feedback
- `POST /api/user/feedback` - Submit feedback for completed service
- `GET /api/user/my-feedback` - Get all user's feedback submissions

### Admin Endpoints

#### Authentication
- `POST /api/admin/register` - Create admin account
- `POST /api/admin/login` - Admin login

#### Service Management
- `GET /api/admin/service-requests` - Get all service requests (with filters)
- `GET /api/admin/service-request/{request_id}` - Get request details
- `PATCH /api/admin/service-request/{request_id}` - Update request (respond, assign, update status)

#### Analytics
- `GET /api/admin/analytics` - Get analytics dashboard data
- `GET /api/admin/technician-performance` - Get all technician performance metrics
- `GET /api/admin/feedback` - Get all feedback submissions

## Database Collections

### users
- User authentication and profile information
- Fields: phone_number, hashed_password, is_active, is_verified, created_at

### admins
- Admin authentication information
- Fields: email, hashed_password, full_name, role, is_active, created_at

### service_requests
- Service request details and status
- Fields: user_id, service_type, name, address, contact_number, preferred_time, issue_description, status, admin_response, technician_name, estimated_arrival_time, created_at, updated_at, completed_at

### feedback
- User feedback and ratings for completed services
- Fields: service_request_id, user_id, technician_name, service_type, rating, comment, created_at

## Configuration

Key configuration options in `.env`:

```env
# MongoDB
MONGODB_URL=mongodb://localhost:27017
DATABASE_NAME=service_request_app

# JWT
SECRET_KEY=your-secret-key-change-this
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=10080

# Zong SMS API
ZONG_API_URL=https://cpaas.zong.com.pk/api/v1/sms
ZONG_API_KEY=your-zong-api-key
ZONG_SENDER_ID=your-sender-id

# OTP
OTP_EXPIRY_MINUTES=5
```

## Security Features

- Password hashing using bcrypt
- JWT token-based authentication
- Role-based access control (User vs Admin)
- OTP verification for user registration
- Secure password requirements (minimum 6 characters)
- Phone number validation for Pakistani numbers

## SMS Notifications

The system sends SMS notifications for:
- OTP verification during registration
- Admin responses to service requests
- Technician assignment and ETA updates

## Future Enhancements

- Real-time notifications using WebSockets
- Image upload for issue documentation
- Payment integration
- Geolocation-based technician assignment
- Push notifications for mobile apps
- Advanced analytics and reporting

## Development Notes

- The OTP service currently prints OTPs to console in development mode
- Uncomment the actual API calls in `otp_service.py` for production
- Update CORS settings in `main.py` for production
- Use Redis for OTP storage in production instead of in-memory storage
- Implement rate limiting for API endpoints
- Add comprehensive error logging

## License

MIT License
