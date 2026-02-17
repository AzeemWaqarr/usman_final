from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from database import connect_to_mongo, close_mongo_connection
from routes import user, admin


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await connect_to_mongo()
    yield
    # Shutdown
    await close_mongo_connection()


app = FastAPI(
    title="Service Request API",
    description="API for plumber and electrician service requests",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware - Allow frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Local development
        "http://localhost:5173",  # Vite dev server
        "https://*.vercel.app",   # Vercel deployments
        "https://*.netlify.app",  # Netlify deployments
        "https://your-custom-domain.com",  # Your custom domain
        "*"  # Allow all origins (remove in production for security)
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(user.router)
app.include_router(admin.router)


@app.get("/")
async def root():
    return {
        "message": "Service Request API",
        "version": "1.0.0",
        "endpoints": {
            "user": "/api/user",
            "admin": "/api/admin",
            "docs": "/docs"
        }
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    import os
    # Use PORT environment variable for deployment (Render, Railway, etc.)
    # Falls back to 8000 for local development
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
