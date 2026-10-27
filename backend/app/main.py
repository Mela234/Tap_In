from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import trends, categories, health, admin, stripe
from app.tasks.email_scheduler import start_email_scheduler
from app.tasks.scheduler import start_news_scheduler
from app.core.database import Base, engine
from app import models  # noqa: F401  (registers every table on Base.metadata)
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
    description="Daily news highlights, six sides at a time",
    version="1.0.0"
)

# CORS middleware (allows frontend to call API)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://tapinpointo.netlify.app"],
    allow_origin_regex=r"http://localhost:\d+",  # local dev servers
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
    
    # Create any missing tables (e.g. highlights on a fresh database)
    Base.metadata.create_all(bind=engine)

    # Start the daily news pipeline
    try:
        start_news_scheduler()
    except Exception as e:
        print(f"⚠️  Failed to initialize news scheduler: {e}")

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
