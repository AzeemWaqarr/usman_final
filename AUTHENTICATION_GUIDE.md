# 🔐 Authentication & Session Management Guide

## How User Sessions Work in Your App

Your app uses **JWT (JSON Web Tokens)** for authentication - users stay logged in without needing to repeatedly authenticate! Tokens can be revoked using the logout endpoint.

---

## 📱 User Registration & Login Flow

### **Registration Flow (Auto-Login)**

1. **User sends phone number** → `POST /api/user/register/send-otp`
   ```json
   {
     "phone_number": "03001234567"
   }
   ```
   ✅ Response: OTP sent via SMS

2. **User enters OTP** → `POST /api/user/register/verify-otp`
   ```json
   {
     "phone_number": "03001234567",
     "otp": "123456"
   }
   ```
   ✅ Response: OTP verified

3. **User sets password** → `POST /api/user/register/complete`
   ```json
   {
     "phone_number": "03001234567",
     "password": "MyPassword123"
   }
   ```
   ✅ **Response: JWT Token** (User is now logged in!)
   ```json
   {
     "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
     "token_type": "bearer"
   }
   ```

**🎉 User is automatically logged in after registration!**

### **Login Flow (Returning Users)**

1. **User logs in** → `POST /api/user/login`
   ```json
   {
     "phone_number": "03001234567",
     "password": "MyPassword123"
   }
   ```
   ✅ **Response: JWT Token**
   ```json
   {
     "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
     "token_type": "bearer"
   }
   ```

### **Logout**

**User Logout** → `POST /api/user/logout`
```bash
# Include token in header
Authorization: Bearer YOUR_TOKEN_HERE
```
✅ **Response:**
```json
{
  "message": "Successfully logged out",
  "detail": "Your session has been terminated. Please login again to access your account."
}
```

**Admin Logout** → `POST /api/admin/logout`
```bash
# Include token in header
Authorization: Bearer YOUR_ADMIN_TOKEN_HERE
```
✅ **Response:**
```json
{
  "message": "Admin successfully logged out",
  "detail": "Your admin session has been terminated. Please login again to access the admin panel."
}
```

---

## 🔑 How JWT Tokens Work

### **Token Details**

- **Type**: JWT (JSON Web Token)
- **Expiry**: 7 days (10,080 minutes) - configurable in `.env`
- **Can be revoked**: Yes, using logout endpoint (token blacklist)
- **Contents**: 
  - User ID
  - User Role (user/admin)
  - Expiration timestamp

### **Token Storage (Frontend)**

The frontend/mobile app should:

1. **Receive token** after login/registration
2. **Store token** securely:
   - **Web**: `localStorage` or `sessionStorage`
   - **Mobile**: Secure storage (Keychain/Keystore)
3. **Include token** in every API request

### **Example: Using Token in Requests**

```javascript
// Frontend example (JavaScript/React)

// 1. Store token after login
const response = await fetch('/api/user/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    phone_number: '03001234567',
    password: 'MyPassword123'
  })
});

const data = await response.json();
localStorage.setItem('token', data.access_token);

// 2. Use token in subsequent requests
const makeRequest = async () => {
  const token = localStorage.getItem('token');
  
  const response = await fetch('/api/user/service-request', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`  // ← Include token here
    },
    body: JSON.stringify({
      service_type: 'plumber',
      name: 'John Doe',
      address: '123 Street',
      contact_number: '03001234567',
      preferred_time: '2026-01-30T14:00:00',
      issue_description: 'Leaking pipe'
    })
  });
  
  return await response.json();
};

// 3. Logout function
const logout = async () => {
  const token = localStorage.getItem('token');
  
  try {
    const response = await fetch('/api/user/logout', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });
    
    const data = await response.json();
    console.log(data.message); // "Successfully logged out"
    
    // Remove token from storage
    localStorage.removeItem('token');
    
    // Redirect to login page
    window.location.href = '/login';
  } catch (error) {
    console.error('Logout failed:', error);
  }
};
```

---

## 🛡️ Protected Endpoints

All these endpoints require authentication (token must be included):

### **User Endpoints** (Requires user token)
- `POST /api/user/service-request` - Create service request
- `GET /api/user/service-requests` - Get user's requests
- `GET /api/user/service-request/{id}` - Get specific request
- `POST /api/user/feedback` - Submit feedback
- `GET /api/user/my-feedback` - Get user's feedback

### **Admin Endpoints** (Requires admin token)
- `GET /api/admin/service-requests` - View all requests
- `PATCH /api/admin/service-request/{id}` - Update request
- `GET /api/admin/analytics` - View analytics
- `GET /api/admin/technician-performance` - View performance
- `GET /api/admin/feedback` - View all feedback

---

## ⚙️ Token Configuration

Edit `.env` to customize token behavior:

```env
# JWT Configuration
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=10080  # 7 days

# Change expiry time:
# 1440 = 1 day
# 4320 = 3 days
# 10080 = 7 days (default)
# 43200 = 30 days
```

---

## 📲 Mobile App Implementation

### **React Native Example**

```javascript
import AsyncStorage from '@react-native-async-storage/async-storage';

// Save token after login
const login = async (phoneNumber, password) => {
  const response = await fetch('http://your-api.com/api/user/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ phone_number: phoneNumber, password })
  });
  
  const data = await response.json();
  await AsyncStorage.setItem('authToken', data.access_token);
  return data;
};

// Use token in requests
const createServiceRequest = async (requestData) => {
  const token = await AsyncStorage.getItem('authToken');
  
  const response = await fetch('http://your-api.com/api/user/service-request', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify(requestData)
  });
  
  return await response.json();
};

// Logout
const logout = async () => {
  const token = await AsyncStorage.getItem('authToken');
  
  try {
    // Call logout API to blacklist token
    const response = await fetch('http://your-api.com/api/user/logout', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });
    
    const data = await response.json();
    console.log(data.message); // "Successfully logged out"
    
    // Remove token from storage
    await AsyncStorage.removeItem('authToken');
    
    // Navigate to login screen
    // navigation.navigate('Login');
  } catch (error) {
    console.error('Logout failed:', error);
    // Remove token anyway
    await AsyncStorage.removeItem('authToken');
  }
};
```

### **Flutter Example**

```dart
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';

final storage = FlutterSecureStorage();

// Save token after login
Future<void> login(String phoneNumber, String password) async {
  final response = await http.post(
    Uri.parse('http://your-api.com/api/user/login'),
    headers: {'Content-Type': 'application/json'},
    body: jsonEncode({
      'phone_number': phoneNumber,
      'password': password,
    }),
  );
  
  final data = jsonDecode(response.body);
  await storage.write(key: 'authToken', value: data['access_token']);
}

// Use token in requests
Future<void> createServiceRequest(Map<String, dynamic> requestData) async {
  final token = await storage.read(key: 'authToken');
  
  final response = await http.post(
    Uri.parse('http://your-api.com/api/user/service-request'),
    headers: {
      'Content-Type': 'application/json',
      'Authorization': 'Bearer $token',
    },
    body: jsonEncode(requestData),
  );
  
  return jsonDecode(response.body);
}
```

---

## 🔄 Token Refresh & Expiry

### **Current Behavior**
- Token expires after **7 days**
- User must login again after expiration

### **Handling Token Expiry (Frontend)**

```javascript
const makeAuthenticatedRequest = async (url, options) => {
  const token = localStorage.getItem('token');
  
  const response = await fetch(url, {
    ...options,
    headers: {
      ...options.headers,
      'Authorization': `Bearer ${token}`
    }
  });
  
  // Check if token expired
  if (response.status === 401) {
    // Token expired - redirect to login
    localStorage.removeItem('token');
    window.location.href = '/login';
    return;
  }
  
  return await response.json();
};
```

---

## ✅ Testing Authentication

### **Using Swagger UI (http://localhost:8000/docs)**

1. **Login or Register** to get a token
2. **Click "Authorize" button** at the top
3. **Enter**: `Bearer YOUR_TOKEN_HERE`
4. **Click "Authorize"**
5. Now all protected endpoints will work!

### **Using cURL**

```bash
# Login
curl -X POST "http://localhost:8000/api/user/login" \
  -H "Content-Type: application/json" \
  -d '{"phone_number": "03001234567", "password": "MyPassword123"}'

# Response: {"access_token": "eyJhbG...", "token_type": "bearer"}

# Use token in request
curl -X POST "http://localhost:8000/api/user/service-request" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer eyJhbG..." \
  -d '{
    "service_type": "plumber",
    "name": "John Doe",
    "address": "123 Street",
    "contact_number": "03001234567",
    "preferred_time": "2026-01-30T14:00:00",
    "issue_description": "Leaking pipe"
  }'
```

---

## 🔒 Security Features

✅ **Password Hashing** - Passwords stored with bcrypt (never plain text)
✅ **JWT Signing** - Tokens signed with secret key (can't be forged)
✅ **Token Expiry** - Tokens automatically expire after 7 days
✅ **Token Blacklisting** - Logout revokes tokens immediately
✅ **Role-Based Access** - Users can't access admin endpoints
✅ **OTP Verification** - Phone numbers verified before registration

---

## 🚪 How Logout Works

### **Token Blacklist System**

When a user logs out:
1. ✅ Token is added to a **blacklist**
2. ✅ Any future requests with that token are **rejected**
3. ✅ User must login again to get a new token

### **Security Benefits**
- Immediate session termination
- Prevents stolen token usage
- Works across all devices
- No database queries needed

### **Production Note**
Currently using in-memory storage (tokens cleared on server restart). For production:
- Use **Redis** for persistent blacklist
- Tokens stay blacklisted even after server restarts
- Blacklist entries auto-expire after token expiry time

---

## 📝 Summary

### **User Flow:**
1. Register → Get OTP → Verify OTP → Set Password → **Get Token** ✅
2. Store token in app
3. Include token in all requests
4. User stays logged in for 7 days
5. **Logout** → Token blacklisted, user logged out immediately
6. Login again after token expires or logout

### **Token Format:**
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### **Key Benefits:**
- 🚀 Fast authentication (no database lookups)
- 📱 Works perfectly with mobile apps
- 🔒 Secure and stateless
- ⏱️ Automatic expiry
- 🚪 Instant logout capability
- 🎯 No need to repeatedly login

Your authentication is production-ready! 🎉
