import os
import stripe
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import trends, categories, health
from dotenv import load_dotenv

load_dotenv()

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

app = FastAPI(
    title="TAPIN API",
    description="Gen Z Trend Mining Platform",
    version="1.0.0"
)

# CORS middleware (allows frontend to call API)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, prefix="/api", tags=["Health"])
app.include_router(categories.router, prefix="/api", tags=["Categories"])
app.include_router(trends.router, prefix="/api", tags=["Trends"])

@app.get("/")
def root():
    return {
        "message": "Welcome to TAPIN API",
        "docs": "/docs",
        "version": "1.0.0"
    }
