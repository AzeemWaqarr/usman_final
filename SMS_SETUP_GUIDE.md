# SMS Setup Guide - Send Real OTPs to Phone Numbers

Your application is currently in **development mode** - OTPs are printed to the console but not sent to phones. Here's how to enable real SMS sending:

---

## ✅ Option 1: Twilio (Recommended for Testing - Works Immediately)

Twilio works in Pakistan and offers free trial credits ($15-20) to test your app.

### Step 1: Create Twilio Account

1. Visit: https://www.twilio.com/try-twilio
2. Sign up with your email
3. Verify your phone number
4. You'll get **free trial credits**

### Step 2: Get Your Credentials

1. Go to: https://console.twilio.com/
2. Find these values on your dashboard:
   - **Account SID** (e.g., `ACxxxxxxxxxxxxxxxxxxxxxxxxxxxx`)
   - **Auth Token** (click to reveal)
   - **Phone Number** (e.g., `+15075007928`)

### Step 3: Update Your `.env` File

```env
# Twilio SMS Configuration (for testing)
ZONG_API_URL=https://api.twilio.com/2010-04-01/Accounts/YOUR_ACCOUNT_SID/Messages.json
ZONG_API_KEY=your_auth_token_here
ZONG_SENDER_ID=your_twilio_phone_number

# Example:
# ZONG_API_URL=https://api.twilio.com/2010-04-01/Accounts/AC1234567890abcdef/Messages.json
# ZONG_API_KEY=your_32_character_auth_token
# ZONG_SENDER_ID=+15075007928
```

### Step 4: Verify Numbers (Trial Mode Only)

⚠️ **Important**: With Twilio trial account, you can only send SMS to **verified numbers**.

1. Go to: https://console.twilio.com/us1/develop/phone-numbers/manage/verified
2. Click "Add a new number"
3. Enter Pakistani phone numbers you want to test with
4. Verify each number via SMS

### Step 5: Test Your App

1. Restart your FastAPI server: `python main.py`
2. Try to register with a **verified** phone number
3. You should receive the OTP on your phone! 📱

### Twilio Pricing (After Trial)

- **Trial**: $15-20 free credits
- **Pay-as-you-go**: ~$0.0079 per SMS to Pakistan
- **No monthly fees** - only pay for what you use

---

## 🇵🇰 Option 2: Zong CPAAS (Best for Production in Pakistan)

Zong is a Pakistani telecom provider with official SMS API service.

### Step 1: Contact Zong

- **Website**: https://cpaas.zong.com.pk/
- **Email**: cpaas@zong.com.pk
- **Phone**: 0310-0310000
- **WhatsApp**: Message them for quick response

### Step 2: Request API Access

Email them with:
```
Subject: SMS API Access Request

Hello,

I am developing a service request application and need SMS API access for sending OTPs and notifications.

Please provide:
- API credentials (API Key)
- API documentation
- Sender ID registration process
- Pricing information

My contact: [Your Phone Number]
Email: [Your Email]

Thank you.
```

### Step 3: Get Credentials

Zong will provide:
- **API URL** (endpoint for sending SMS)
- **API Key** (authentication token)
- **Sender ID** (your brand name/number)

### Step 4: Update `.env` File

```env
# Zong SMS Configuration
ZONG_API_URL=https://cpaas.zong.com.pk/api/v1/sms
ZONG_API_KEY=your_zong_api_key_here
ZONG_SENDER_ID=YourBrandName
```

### Step 5: Test

The code will automatically detect you're using Zong and send SMS accordingly.

### Zong Pricing

- **Bulk SMS rates**: Usually PKR 0.15 - 0.30 per SMS
- **No trial** - requires direct contract
- **Monthly minimum** may apply

---

## 📋 Alternative SMS Providers in Pakistan

### 1. **Jazz SMS API**
- Website: https://jazz.com.pk/business/sms-solutions
- Good for bulk SMS
- Competitive pricing

### 2. **Telenor Bulk SMS**
- Website: https://www.telenor.com.pk/business/sms-solutions
- Reliable service
- Good coverage

### 3. **Veevo Tech**
- Website: https://veevotech.com/
- SMS gateway aggregator
- Works with all Pakistani networks

### 4. **SMS.to**
- Website: https://sms.to/
- International service that works in Pakistan
- Pay-as-you-go pricing

---

## 🔧 Current Development Mode

Right now, your app is in **development mode**:

✅ **What works:**
- OTP generation
- Phone number validation
- All API endpoints
- Database storage
- User registration flow

📱 **What happens with OTPs:**
- OTPs are generated correctly
- They are printed to the console/terminal
- You can copy them from the console and use them to test
- The app works exactly as it would with real SMS

**Console Output Example:**
```
OTP for +923085253374: 280649
OTP for +923261467086: 842944
```

---

## ⚙️ Your Updated Code

I've updated your `otp_service.py` to:

✅ **Automatically detect** if you're using Twilio or Zong
✅ **Send real SMS** when credentials are configured
✅ **Fall back to console** if SMS fails (for development)
✅ **Support both OTP and notification** SMS

No code changes needed - just update your `.env` file!

---

## 🎯 Recommended Path

**For immediate testing:**
1. Use **Twilio** (5 minutes setup, works right away)
2. Verify 2-3 phone numbers
3. Test your entire app flow
4. Use free trial credits

**For production (Pakistan):**
1. Contact **Zong CPAAS** while testing with Twilio
2. Get official API access (takes 2-7 days)
3. Switch to Zong for production
4. Benefit from local rates and coverage

---

## 📞 Need Help?

Your SMS service will work as soon as you:
1. Choose a provider (Twilio for testing, Zong for production)
2. Get API credentials
3. Update 3 lines in your `.env` file
4. Restart the server

The code is ready - you just need the credentials! 🚀
