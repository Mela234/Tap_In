from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.core.database import SessionLocal
from app.models.highlight import Highlight
from app.news.feeds import TOPICS, TOPIC_LABELS
from datetime import date, datetime, timedelta
from firebase_admin import firestore

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def format_highlight(h: Highlight) -> dict:
    """Shape a highlight like the trend objects the frontend and emails expect"""
    sources = h.sources or []
    return {
        "id": h.id,
        "type": "highlight",
        "topic": h.topic,
        "category": TOPIC_LABELS.get(h.topic, h.topic.title()),
        "title": h.title,
        "description": h.gist,
        "why_it_matters": h.why_it_matters,
        "relevance_score": min(1.0, (h.coverage or 1) / 4),
        "coverage": h.coverage,
        "source": sources[0]["name"] if sources else None,
        "sources": sources,
        "source_links": [s["url"] for s in sources],
        "edition": h.edition.isoformat(),
        "created_at": h.created_at.isoformat() if h.created_at else None,
    }


def get_weekly_highlights(db: Session, limit: int = 20) -> dict:
    """The biggest stories from the last 7 daily editions, most widely covered first"""
    week_end = date.today()
    week_start = week_end - timedelta(days=7)

    rows = db.query(Highlight).filter(
        Highlight.edition > week_start
    ).order_by(
        Highlight.coverage.desc(), Highlight.edition.desc(), Highlight.rank
    ).all()

    trends, seen_titles = [], set()
    for h in rows:
        if h.title in seen_titles:
            continue
        seen_titles.add(h.title)
        trends.append(format_highlight(h))
        if len(trends) == limit:
            break

    return {
        "week_start": week_start.isoformat(),
        "week_end": week_end.isoformat(),
        "trends": trends,
    }


@router.get("/trends/weekly")
def get_weekly_trends(db: Session = Depends(get_db)):
    """Get the week's top highlights across every topic"""
    return get_weekly_highlights(db)


@router.get("/trends/hexagon")
def get_hexagon_trends(db: Session = Depends(get_db)):
    """Get the latest daily edition grouped into the six hexagon topics"""

    latest = db.query(Highlight.edition).order_by(Highlight.edition.desc()).first()
    topics = {topic: [] for topic in TOPICS}

    if not latest:
        return {"edition": None, "topics": topics}

    rows = db.query(Highlight).filter(
        Highlight.edition == latest.edition
    ).order_by(Highlight.rank).all()

    for h in rows:
        topics.setdefault(h.topic, []).append(format_highlight(h))

    return {"edition": latest.edition.isoformat(), "topics": topics}


@router.get("/trends/archive")
def get_archive(db: Session = Depends(get_db), page: int = 1, limit: int = 10):
    """Get every past highlight, newest edition first"""

    page = max(1, page)
    total = db.query(Highlight).count()
    rows = db.query(Highlight).order_by(
        Highlight.edition.desc(), Highlight.topic, Highlight.rank
    ).offset((page - 1) * limit).limit(limit).all()

    return {
        "page": page,
        "total_pages": max(1, -(-total // limit)),
        "trends": [format_highlight(h) for h in rows],
    }


@router.get("/trends/archive/{week_start}")
def get_archive_week(week_start: str, db: Session = Depends(get_db)):
    """Get the highlights published in a specific week"""

    try:
        start_date = datetime.strptime(week_start, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
    end_date = start_date + timedelta(days=7)

    rows = db.query(Highlight).filter(
        Highlight.edition >= start_date,
        Highlight.edition < end_date,
    ).order_by(Highlight.edition, Highlight.topic, Highlight.rank).all()

    return {
        "week_start": week_start,
        "week_end": end_date.isoformat(),
        "trend_count": len(rows),
        "trends": [format_highlight(h) for h in rows],
    }


@router.get("/trends/category/{category}")
def get_trends_by_category(category: str, db: Session = Depends(get_db)):
    """Get this week's highlights for one hexagon topic"""

    topic = category.lower()
    if topic not in TOPICS:
        raise HTTPException(status_code=404, detail=f"Unknown category: {category}")

    rows = db.query(Highlight).filter(
        Highlight.topic == topic,
        Highlight.edition > date.today() - timedelta(days=7),
    ).order_by(Highlight.edition.desc(), Highlight.rank).all()

    return {
        "category": topic,
        "trends": [format_highlight(h) for h in rows],
    }


@router.get("/trends/{trend_id}")
def get_trend_by_id(trend_id: int, db: Session = Depends(get_db)):
    """Get one highlight"""

    highlight = db.query(Highlight).filter(Highlight.id == trend_id).first()

    if not highlight:
        raise HTTPException(status_code=404, detail="Trend not found")

    return format_highlight(highlight)


class EmailSubscriptionRequest(BaseModel):
    email: str
    subscribe: bool


@router.post("/email/subscribe")
def subscribe_to_email_digest(request: EmailSubscriptionRequest):
    """Subscribe or unsubscribe from weekly email digest (Firestore)"""
    try:
        firestore_db = firestore.client()
        
        users_ref = firestore_db.collection('users').where('email', '==', request.email).stream()
        
        user_found = False
        for user_doc in users_ref:
            firestore_db.collection('users').document(user_doc.id).update({
                'email_notifications': request.subscribe
            })
            user_found = True
            break
        
        if not user_found:
            raise HTTPException(status_code=404, detail="User not found. Please sign up first.")
        
        status = "subscribed" if request.subscribe else "unsubscribed"
        return {
            "success": True,
            "message": f"Successfully {status} from email digest",
            "email": request.email,
            "email_notifications": request.subscribe
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update subscription: {str(e)}"
        )


@router.get("/email/subscription-status/{email}")
def get_subscription_status(email: str):
    """Get email subscription status for a user (Firestore)"""
    try:
        firestore_db = firestore.client()
        
        users_ref = firestore_db.collection('users').where('email', '==', email).stream()
        
        for user_doc in users_ref:
            user_data = user_doc.to_dict()
            return {
                "email": email,
                "email_notifications": user_data.get('email_notifications', True),
                "last_email_sent": user_data.get('last_email_sent').isoformat() if user_data.get('last_email_sent') else None
            }
        
        return {
            "email": email,
            "email_notifications": False,
            "last_email_sent": None
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get subscription status: {str(e)}"
        )


@router.post("/email/test-send/{email}")
def test_send_digest_email(email: str):
    """Test endpoint to send a digest email immediately (for testing purposes)"""
    try:
        from app.tasks.email_scheduler import test_send_digest_email as send_test
        
        success = send_test(email)
        
        if success:
            return {
                "success": True,
                "message": f"Test email sent successfully to {email}"
            }
        else:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to send test email to {email}"
            )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error sending test email: {str(e)}"
        )