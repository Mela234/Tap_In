from fastapi import APIRouter, HTTPException, Depends, Header
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime, timedelta
from pydantic import BaseModel
from app.core.database import get_db
from app.models.trend import Trend
import firebase_admin
from firebase_admin import auth, firestore

router = APIRouter()


# Verify Firebase token and check if user is admin
async def verify_admin(authorization: str = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid authorization header")
    
    token = authorization.replace("Bearer ", "")
    
    try:
        # Verify Firebase token
        decoded_token = auth.verify_id_token(token)
        uid = decoded_token['uid']
        
        db = firestore.client()
        user_doc = db.collection('users').document(uid).get()
        
        if not user_doc.exists:
            raise HTTPException(status_code=403, detail="User not found")
        
        user_data = user_doc.to_dict()
        
        if not user_data.get('isAdmin', False):
            raise HTTPException(status_code=403, detail="Not authorized - admin access required")
        
        return {
            "uid": uid,
            "email": decoded_token.get('email'),
            "isAdmin": True
        }
    
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")


class CreateTrendRequest(BaseModel):
    title: str
    description: str
    category_id: Optional[int] = None
    why_it_matters: Optional[str] = None
    how_to_talk_about_it: Optional[str] = None
    relevance_score: float = 0.85
    sources: Optional[str] = None
    week_start: Optional[str] = None
    week_end: Optional[str] = None


@router.post("/admin/trends")
async def create_trend(
    trend_data: CreateTrendRequest,
    db: Session = Depends(get_db),
    admin_user: dict = Depends(verify_admin)
):
    """Create a new trend (admin only)"""
    
    if not trend_data.week_start:
        week_start = datetime.utcnow()
    else:
        week_start = datetime.strptime(trend_data.week_start, "%Y-%m-%d")
    
    if not trend_data.week_end:
        week_end = week_start + timedelta(days=7)
    else:
        week_end = datetime.strptime(trend_data.week_end, "%Y-%m-%d")
    
    new_trend = Trend(
        title=trend_data.title,
        description=trend_data.description,
        why_it_matters=trend_data.why_it_matters,
        how_to_talk_about_it=trend_data.how_to_talk_about_it,
        category_id=trend_data.category_id,
        relevance_score=trend_data.relevance_score,
        sources=trend_data.sources,
        week_start=week_start,
        week_end=week_end
    )
    
    db.add(new_trend)
    db.commit()
    db.refresh(new_trend)
    
    return {
        "success": True,
        "message": "Trend created successfully",
        "trend": {
            "id": new_trend.id,
            "title": new_trend.title,
            "created_at": new_trend.created_at.isoformat()
        }
    }


@router.get("/admin/trends")
async def get_all_trends(
    db: Session = Depends(get_db),
    admin_user: dict = Depends(verify_admin)
):
    """Get all trends (admin only)"""
    
    trends = db.query(Trend).order_by(Trend.created_at.desc()).all()
    
    return {
        "total": len(trends),
        "trends": [
            {
                "id": t.id,
                "title": t.title,
                "description": t.description,
                "category_id": t.category_id,
                "created_at": t.created_at.isoformat()
            }
            for t in trends
        ]
    }


@router.delete("/admin/trends/{trend_id}")
async def delete_trend(
    trend_id: int,
    db: Session = Depends(get_db),
    admin_user: dict = Depends(verify_admin)
):
    """Delete a trend (admin only)"""
    
    trend = db.query(Trend).filter(Trend.id == trend_id).first()
    
    if not trend:
        raise HTTPException(status_code=404, detail="Trend not found")
    
    title = trend.title
    db.delete(trend)
    db.commit()
    
    return {"success": True, "message": f"Trend '{title}' deleted"}