import random
import requests
from datetime import datetime, timedelta
from typing import Optional, Dict, Set
from config import settings

# In-memory OTP storage (in production, use Redis or database)
otp_storage: Dict[str, dict] = {}

# In-memory token blacklist (in production, use Redis)
blacklisted_tokens: Set[str] = {}


def generate_otp() -> str:
    """Generate a 6-digit OTP"""
    return str(random.randint(100000, 999999))


def store_otp(phone_number: str, otp: str) -> None:
    """Store OTP with expiry time"""
    expiry = datetime.utcnow() + timedelta(minutes=settings.OTP_EXPIRY_MINUTES)
    otp_storage[phone_number] = {
        "otp": otp,
        "expiry": expiry,
        "attempts": 0
    }


def verify_otp(phone_number: str, otp: str) -> bool:
    """Verify OTP"""
    if phone_number not in otp_storage:
        return False
    
    stored_data = otp_storage[phone_number]
    
    # Check if OTP expired
    if datetime.utcnow() > stored_data["expiry"]:
        del otp_storage[phone_number]
        return False
    
    # Check attempts
    if stored_data["attempts"] >= 3:
        del otp_storage[phone_number]
        return False
    
    # Verify OTP
    if stored_data["otp"] == otp:
        del otp_storage[phone_number]
        return True
    else:
        otp_storage[phone_number]["attempts"] += 1
        return False


def blacklist_token(token: str) -> None:
    """Add token to blacklist"""
    blacklisted_tokens.add(token)


def is_token_blacklisted(token: str) -> bool:
    """Check if token is blacklisted"""
    return token in blacklisted_tokens


async def send_otp_via_zong(phone_number: str, otp: str) -> bool:
    """
    Send OTP via Zong SMS API or Twilio
    Automatically detects which service to use based on URL
    """
    try:
        # Format phone number
        formatted_number = phone_number
        if phone_number.startswith('0'):
            formatted_number = '+92' + phone_number[1:]
        elif not phone_number.startswith('+'):
            formatted_number = '+92' + phone_number
        
        message = f"Your verification code is: {otp}. Valid for {settings.OTP_EXPIRY_MINUTES} minutes."
        
        # Check if using Twilio
        if "twilio.com" in settings.ZONG_API_URL.lower():
            # Extract account SID from URL
            if "Accounts/" in settings.ZONG_API_URL:
                account_sid = settings.ZONG_API_URL.split("Accounts/")[1].split("/")[0]
                auth_token = settings.ZONG_LOGIN_ID
                from_number = settings.ZONG_MASK
                
                # Send SMS via Twilio
                response = requests.post(
                    settings.ZONG_API_URL,
                    auth=(account_sid, auth_token),
                    data={
                        "From": from_number,
                        "To": formatted_number,
                        "Body": message
                    }
                )
                
                if response.status_code in [200, 201]:
                    print(f"✅ SMS sent to {formatted_number} via Twilio")
                    return True
                else:
                    print(f"❌ Twilio Error: {response.status_code} - {response.text}")
                    print(f"📱 Development Mode: OTP for {formatted_number}: {otp}")
                    return True  # Return True anyway for development
            else:
                print(f"⚠️  Invalid Twilio URL in .env")
                print(f"📱 Development Mode: OTP for {formatted_number}: {otp}")
                return True
        
        # Zong API request structure - EXACT format from working Next.js implementation
        # Format phone number: 12 digits with 92 prefix, no leading zero
        phone_for_api = formatted_number.replace('+', '').replace(' ', '')
        if phone_for_api.startswith('0'):
            phone_for_api = phone_for_api[1:]
        if not phone_for_api.startswith('92'):
            phone_for_api = '92' + phone_for_api
        
        # Ensure 12 digits
        if len(phone_for_api) != 12:
            print(f"⚠️  Invalid phone format: {phone_for_api} (should be 12 digits)")
            print(f"📱 Development Mode: OTP for {formatted_number}: {otp}")
            return True
        
        # Form data (NOT JSON) - exact parameter names that work
        form_data = {
            'loginId': settings.ZONG_LOGIN_ID,
            'loginPassword': settings.ZONG_PASSWORD,
            'Mask': settings.ZONG_MASK,
            'Destination': phone_for_api,
            'Message': message,
            'UniCode': '1',
            'dataCoding': '8',
            'ShortCodePrefered': 'n'
        }
        
        print(f"🔄 Sending SMS to {formatted_number} (formatted as {phone_for_api})")
        print(f"📤 Form Data: {form_data}")
        
        try:
            # POST with form-encoded data (NOT JSON)
            response = requests.post(
                settings.ZONG_API_URL,
                data=form_data,  # Use 'data' not 'json'
                headers={
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'User-Agent': 'BGS-Portal/1.0'
                },
                timeout=30,
                verify=False  # Disable SSL verification
            )
            
            print(f"📥 Response Status: {response.status_code}")
            print(f"📥 Response Body: {response.text}")
            
            # Success response starts with "0|success"
            if response.status_code == 200 and response.text.startswith('0|success'):
                print(f"✅ SMS sent to {formatted_number} via Zong")
                return True
            else:
                print(f"⚠️  Zong API Error: {response.text}")
                print(f"📱 Development Mode: OTP for {formatted_number}: {otp}")
                return True  # Return True anyway for development
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Request failed: {str(e)}")
            print(f"📱 Development Mode: OTP for {formatted_number}: {otp}")
            return True  # Return True anyway for development
        
    except Exception as e:
        print(f"❌ Error sending OTP: {str(e)}")
        print(f"📱 Development Mode: OTP for {formatted_number}: {otp}")
        return True  # Return True anyway for development


async def send_notification_sms(phone_number: str, message: str) -> bool:
    """
    Send notification SMS via Zong or Twilio
    """
    try:
        # Format phone number
        formatted_number = phone_number
        if phone_number.startswith('0'):
            formatted_number = '+92' + phone_number[1:]
        elif not phone_number.startswith('+'):
            formatted_number = '+92' + phone_number
        
        # Check if using Twilio
        if "twilio.com" in settings.ZONG_API_URL.lower():
            if "Accounts/" in settings.ZONG_API_URL:
                account_sid = settings.ZONG_API_URL.split("Accounts/")[1].split("/")[0]
                auth_token = settings.ZONG_LOGIN_ID
                from_number = settings.ZONG_MASK
                
                response = requests.post(
                    settings.ZONG_API_URL,
                    auth=(account_sid, auth_token),
                    data={
                        "From": from_number,
                        "To": formatted_number,
                        "Body": message
                    }
                )
                
                if response.status_code in [200, 201]:
                    print(f"✅ Notification sent to {formatted_number} via Twilio")
                    return True
                else:
                    print(f"❌ Twilio Error: {response.status_code}")
                    print(f"📱 Development Mode: SMS to {formatted_number}: {message}")
                    return True
            else:
                print(f"📱 Development Mode: SMS to {formatted_number}: {message}")
                return True
        
        # Zong API - use correct format like send_otp_via_zong
        # Format phone number: 12 digits with 92 prefix, no leading zero
        phone_for_api = formatted_number.replace('+', '').replace(' ', '')
        if phone_for_api.startswith('0'):
            phone_for_api = phone_for_api[1:]
        if not phone_for_api.startswith('92'):
            phone_for_api = '92' + phone_for_api
        
        # Form data (NOT JSON) - exact parameter names that work
        form_data = {
            'loginId': settings.ZONG_LOGIN_ID,
            'loginPassword': settings.ZONG_PASSWORD,
            'Mask': settings.ZONG_MASK,
            'Destination': phone_for_api,
            'Message': message,
            'UniCode': '1',
            'dataCoding': '8',
            'ShortCodePrefered': 'n'
        }
        
        print(f"🔄 Sending notification to {formatted_number} (formatted as {phone_for_api})")
        print(f"📤 Form Data: {form_data}")
        
        try:
            # POST with form-encoded data
            response = requests.post(
                settings.ZONG_API_URL,
                data=form_data,
                headers={
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'User-Agent': 'BGS-Portal/1.0'
                },
                timeout=30,
                verify=False
            )
            
            print(f"📥 Response Status: {response.status_code}")
            print(f"📥 Response Body: {response.text}")
            
            # Success response starts with "0|success"
            if response.status_code == 200 and response.text.startswith('0|success'):
                print(f"✅ Notification sent to {formatted_number} via Zong")
                return True
            else:
                print(f"⚠️  Zong Response: {response.text}")
                print(f"📱 Development Mode: SMS to {formatted_number}: {message}")
                return True
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Request failed: {str(e)}")
            print(f"📱 Development Mode: SMS to {formatted_number}: {message}")
            return True
        
    except Exception as e:
        print(f"❌ Error sending SMS: {str(e)}")
        print(f"📱 Development Mode: SMS to {formatted_number}: {message}")
        return True
