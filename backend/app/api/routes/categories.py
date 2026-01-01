from fastapi import APIRouter

router = APIRouter()

@router.get("/categories")
def get_categories():
    """Get all trend categories"""
    return {
        "categories": [
            {"id": 1, "name": "Music", "count": 12},
            {"id": 2, "name": "Slang", "count": 18},
            {"id": 3, "name": "TikTok", "count": 15},
            {"id": 4, "name": "Memes", "count": 10},
            {"id": 5, "name": "Fashion", "count": 8},
            {"id": 6, "name": "Gaming", "count": 6},
            {"id": 7, "name": "Social Issues", "count": 5}
        ]
    }