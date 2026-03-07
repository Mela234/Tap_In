from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import trends, categories, health, admin, stripe
from app.tasks.email_scheduler import start_email_scheduler
import firebase_admin
from firebase_admin import credentials

# Initialize Firebase Admin SDK
try:
    cred = credentials.Certificate("serviceAccountKey.json")
    firebase_admin.initialize_app(cred)
    print("✅ Firebase Admin initialized successfully")
except Exception as e:
    print(f"⚠️  Firebase Admin initialization failed: {e}")
    print("   Admin endpoints will not work without Firebase Admin SDK")

app = FastAPI(
    title="TAPIN API",
    description="Gen Z Trend Mining Platform",
    version="1.0.0"
)

# CORS middleware (allows frontend to call API)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*", "https://tapinpointo.netlify.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, prefix="/api", tags=["Health"])
app.include_router(categories.router, prefix="/api", tags=["Categories"])
app.include_router(trends.router, prefix="/api", tags=["Trends"])
app.include_router(admin.router, prefix="/api", tags=["Admin"]) 
app.include_router(
    stripe.router,
    prefix="/api",
    tags=["Stripe"]
)

# Initialize email scheduler on startup
@app.on_event("startup")
async def startup_event():
    """Initialize background tasks on application startup"""
    print("\n🚀 Starting TAPIN application...")
    
    # Start email scheduler
    try:
        start_email_scheduler()
        print("✅ Email scheduler initialized successfully")
    except Exception as e:
        print(f"⚠️  Failed to initialize email scheduler: {e}")

@app.get("/")
def root():
    return {
        "message": "Welcome to TAPIN API",
        "docs": "/docs",
        "version": "1.0.0"
    }