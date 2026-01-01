from fastapi import APIRouter

router = APIRouter()

@router.get("/health")
def health_check():
    """API health check"""
    return {
        "status": "ok",
        "version": "1.0.0",
        "service": "TAPIN API"
    }