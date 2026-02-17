# Deployment Guide - Go Sargodha API

## 🚀 Quick Deploy

Your FastAPI backend is ready to deploy to:
- ✅ **Render** (Recommended)
- ✅ **Railway**
- ✅ **Heroku**

---

## Option 1: Deploy to Render (Free Tier)

### Step 1: Push to GitHub

```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/yourusername/go-sargodha-api.git
git push -u origin main
```

### Step 2: Deploy on Render

1. Go to [render.com](https://render.com) and sign up with GitHub
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub repository
4. Render will auto-detect `render.yaml`
5. Click **"Create Web Service"**

### Step 3: Set Environment Variables

In Render Dashboard → Your Service → Environment:

**Required Secret Variables:**
- `MONGODB_URL`: `mongodb+srv://usmansss753_db_user:%40Premium2020@cluster0.wchqypx.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0`
- `ZONG_LOGIN_ID`: `923115995310`
- `ZONG_PASSWORD`: `Bg$@0987`
- `ADMIN_DEFAULT_PASSWORD`: Your admin password

**Auto-set Variables (already in render.yaml):**
- DATABASE_NAME
- SECRET_KEY (auto-generated)
- ALGORITHM
- ZONG_API_URL
- ZONG_MASK
- etc.

### Step 4: Deploy

Render will automatically deploy. Check deployment logs for any errors.

**Your API will be live at:** `https://go-sargodha-api.onrender.com`

---

## Option 2: Deploy to Railway (Free 500h/month)

### Step 1: Push to GitHub (same as above)

### Step 2: Deploy on Railway

1. Go to [railway.app](https://railway.app)
2. Sign up with GitHub
3. Click **"New Project"** → **"Deploy from GitHub repo"**
4. Select your repository
5. Railway auto-detects `railway.json`

### Step 3: Add Environment Variables

In Railway Dashboard → Your Project → Variables:

Add all variables from your `.env` file:
```
MONGODB_URL=mongodb+srv://...
DATABASE_NAME=service_request_app
SECRET_KEY=Nb-frIY9Aj8gdBUlCoSvT9BVJ070UHRs6ZpOXvvxrVI
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=10080
ZONG_API_URL=https://cbs.zong.com.pk/reachrestapi/home/SendQuickSMS
ZONG_LOGIN_ID=923115995310
ZONG_PASSWORD=Bg$@0987
ZONG_MASK=BGS
ADMIN_DEFAULT_EMAIL=admin@serviceapp.com
ADMIN_DEFAULT_PASSWORD=admin123
OTP_EXPIRY_MINUTES=5
```

### Step 4: Deploy

Railway will automatically deploy.

**Your API will be live at:** `https://your-app.railway.app`

---

## Option 3: Deploy to Heroku

### Step 1: Install Heroku CLI

```bash
# Windows (use PowerShell)
winget install Heroku.HerokuCLI
```

### Step 2: Deploy

```bash
heroku login
heroku create go-sargodha-api
git push heroku main
```

### Step 3: Set Environment Variables

```bash
heroku config:set MONGODB_URL="mongodb+srv://..."
heroku config:set ZONG_LOGIN_ID="923115995310"
heroku config:set ZONG_PASSWORD="Bg$@0987"
# ... add all other env variables
```

**Your API will be live at:** `https://go-sargodha-api.herokuapp.com`

---

## 📋 Post-Deployment Checklist

After deployment, test these endpoints:

1. **Health Check**: `https://your-url.com/health`
   - Should return: `{"status": "healthy"}`

2. **API Docs**: `https://your-url.com/docs`
   - Interactive Swagger UI

3. **Root Endpoint**: `https://your-url.com/`
   - Should return API info

4. **Send OTP Test**: `POST https://your-url.com/api/user/register/send-otp`
   ```json
   {
     "phone_number": "03176743537"
   }
   ```

---

## 🔧 Troubleshooting

### Issue: MongoDB Connection Failed
- Check if MongoDB Atlas IP whitelist includes `0.0.0.0/0` (allow all)
- Verify `MONGODB_URL` is correctly set in environment variables

### Issue: Application Crash on Startup
- Check deployment logs
- Ensure all required environment variables are set
- Verify `requirements.txt` has all dependencies

### Issue: SMS Not Sending
- Verify Zong credentials in environment variables
- Check Zong API logs in deployment console
- Ensure Zong account has sufficient balance

---

## 🌐 Custom Domain (Optional)

### For Render:
1. Go to Settings → Custom Domains
2. Add your domain
3. Update DNS records as instructed

### For Railway:
1. Go to Settings → Domains
2. Add custom domain
3. Update DNS records

---

## 📊 Monitoring

### Render:
- View logs: Dashboard → Your Service → Logs
- Metrics: Dashboard → Metrics

### Railway:
- View logs: Project → Deployments → View Logs
- Metrics: Project → Metrics

---

## 🔄 Updates & Redeployment

For future updates:

```bash
git add .
git commit -m "Your update message"
git push origin main
```

Render/Railway will auto-deploy on push!

---

## 💡 Free Tier Limitations

**Render Free:**
- Spins down after 15 min inactivity
- First request after sleep: ~30 seconds
- 750 hours/month

**Railway Free:**
- 500 hours/month
- $5 free credit/month
- No sleep time

**Heroku Free:**
- Deprecated (paid plans only)

---

## 📞 Support

If you encounter issues:
1. Check deployment logs
2. Verify environment variables
3. Test MongoDB connection string locally
4. Check Zong API credentials

**API Documentation:** `https://your-url.com/docs`

---

## ✅ Success!

Your API is now live and ready to handle requests! 🎉

Test it: `https://your-deployed-url.com/docs`
