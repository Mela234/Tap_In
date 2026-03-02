from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import Optional
from app.core.database import SessionLocal
from app.models.raw_data import RawData
from datetime import datetime, timedelta

router = APIRouter()

# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/trends/weekly")
def get_weekly_trends(db: Session = Depends(get_db)):
    """Get current week's trending topics from scraped data"""
    
    raw_data = db.query(RawData).order_by(
        RawData.collected_at.desc()
    ).limit(50).all()
    
    if not raw_data:
        return {
            "week_start": datetime.utcnow().strftime("%Y-%m-%d"),
            "week_end": datetime.utcnow().strftime("%Y-%m-%d"),
            "trends": []
        }
    
    # Convert raw data to trend format
    trends = []
    trend_id = 1
    
    for item in raw_data[:20]:  # Return top 20
        trend = format_raw_data_as_trend(item, trend_id)
        if trend:
            trends.append(trend)
            trend_id += 1
    
    return {
        "week_start": (datetime.utcnow() - timedelta(days=7)).strftime("%Y-%m-%d"),
        "week_end": datetime.utcnow().strftime("%Y-%m-%d"),
        "trends": trends
    }


# ARCHIVE ROUTES - MUST COME BEFORE /{trend_id}
@router.get("/trends/archive")
def get_archive(db: Session = Depends(get_db), page: int = 1, limit: int = 10):
    """Get archive of past data"""
    
    offset = (page - 1) * limit
    
    raw_data = db.query(RawData).order_by(
        RawData.collected_at.desc()
    ).offset(offset).limit(limit).all()
    
    # Format as trends (same as weekly)
    trends = []
    for idx, item in enumerate(raw_data, start=offset + 1):
        trend = format_raw_data_as_trend(item, idx)
        if trend:
            trends.append(trend)
    
    return {
        "page": page,
        "total_pages": 1,
        "trends": trends
    }


@router.get("/trends/archive/{week_start}")
def get_archive_week(week_start: str, db: Session = Depends(get_db)):
    """Get trends for a specific week"""
    
    # Parse week_start
    try:
        start_date = datetime.strptime(week_start, "%Y-%m-%d")
        end_date = start_date + timedelta(days=7)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
    
    # Query data from that week
    raw_data = db.query(RawData).filter(
        RawData.collected_at >= start_date,
        RawData.collected_at < end_date
    ).limit(20).all()
    
    trends = []
    for idx, item in enumerate(raw_data, 1):
        trend = format_raw_data_as_trend(item, idx)
        if trend:
            trends.append(trend)
    
    return {
        "week_start": week_start,
        "week_end": end_date.strftime("%Y-%m-%d"),
        "trend_count": len(trends),
        "trends": trends
    }


@router.get("/trends/category/{category}")
def get_trends_by_category(category: str, db: Session = Depends(get_db)):
    """Get trends filtered by category"""
    
    # Map category to source
    source_map = {
        "slang": "urban_dictionary",
        "reddit": "reddit",
        "youtube": "youtube",
        "news": ["buzzfeed", "complex", "thecut", "refinery29"],
        "trending": "google_trends"
    }
    
    source = source_map.get(category.lower())
    
    if not source:
        raise HTTPException(status_code=404, detail=f"Unknown category: {category}")
    
    # Query database
    if isinstance(source, list):
        raw_data = db.query(RawData).filter(RawData.source.in_(source)).limit(20).all()
    else:
        raw_data = db.query(RawData).filter(RawData.source == source).limit(20).all()
    
    if not raw_data:
        return {
            "category": category,
            "trends": []
        }
    
    # Format trends
    trends = []
    for idx, item in enumerate(raw_data, 1):
        trend = format_raw_data_as_trend(item, idx)
        if trend:
            trends.append(trend)
    
    return {
        "category": category,
        "trends": trends
    }


# DYNAMIC ROUTE - MUST COME LAST
@router.get("/trends/{trend_id}")
def get_trend_by_id(trend_id: int, db: Session = Depends(get_db)):
    """Get detailed information about a specific trend"""
    
    # Get raw data by ID
    raw_data = db.query(RawData).filter(RawData.id == trend_id).first()
    
    if not raw_data:
        raise HTTPException(status_code=404, detail="Trend not found")
    
    trend = format_raw_data_as_trend(raw_data, trend_id)
    return trend


def format_raw_data_as_trend(raw_data: RawData, trend_id: int):
    """Convert raw_data to trend format"""
    
    # Determine trend type based on source
    if raw_data.source == "urban_dictionary":
        return {
            "id": trend_id,
            "type": "slang",
            "title": raw_data.extra_data.get("word", "Unknown"),
            "category": "Slang",
            "description": raw_data.extra_data.get("definition", raw_data.content)[:200],
            "relevance_score": 0.85,
            "source": raw_data.source,
            "source_links": [raw_data.url] if raw_data.url else [],
            "example_usage": [raw_data.extra_data.get("example", "")],
            "upvotes": raw_data.extra_data.get("upvotes", "0"),
            "created_at": raw_data.collected_at.isoformat()
        }
    
    elif raw_data.source == "reddit":
        return {
            "id": trend_id,
            "type": "post",
            "title": raw_data.content[:100],  # Post title
            "category": "Reddit",
            "description": raw_data.content,
            "relevance_score": 0.80,
            "source": raw_data.source,
            "source_links": [raw_data.url] if raw_data.url else [],
            "subreddit": raw_data.extra_data.get("subreddit", "unknown"),
            "upvotes": raw_data.extra_data.get("score", "0"),
            "comments": raw_data.extra_data.get("comments", "0"),
            "created_at": raw_data.collected_at.isoformat()
        }
    
    elif raw_data.source == "youtube":
        title_parts = raw_data.content.split('\n')
        title = title_parts[0] if title_parts else "Unknown"
        
        return {
            "id": trend_id,
            "type": "video",
            "title": title[:100],
            "category": "YouTube",
            "description": raw_data.content,
            "relevance_score": 0.88,
            "source": raw_data.source,
            "source_links": [raw_data.url] if raw_data.url else [],
            "channel": raw_data.extra_data.get("channel_title", "Unknown"),
            "views": raw_data.extra_data.get("views", 0),
            "likes": raw_data.extra_data.get("likes", 0),
            "created_at": raw_data.collected_at.isoformat()
        }
    
    elif raw_data.source in ["buzzfeed", "complex", "thecut", "refinery29"]:
        return {
            "id": trend_id,
            "type": "article",
            "title": raw_data.content[:100],
            "category": "News",
            "description": raw_data.content,
            "relevance_score": 0.75,
            "source": raw_data.source,
            "source_links": [raw_data.url] if raw_data.url else [],
            "created_at": raw_data.collected_at.isoformat()
        }
    
    elif raw_data.source == "google_trends":
        return {
            "id": trend_id,
            "type": "keyword",
            "title": raw_data.content,
            "category": "Trending",
            "description": f"Search interest: {raw_data.extra_data.get('avg_interest_score', 0)}/100",
            "relevance_score": raw_data.extra_data.get('avg_interest_score', 0) / 100,
            "source": raw_data.source,
            "interest_score": raw_data.extra_data.get('avg_interest_score', 0),
            "created_at": raw_data.collected_at.isoformat()
        }
    
    else:
        # Generic format for other sources
        return {
            "id": trend_id,
            "type": "general",
            "title": raw_data.content[:100],
            "category": "General",
            "description": raw_data.content,
            "relevance_score": 0.70,
            "source": raw_data.source,
            "source_links": [raw_data.url] if raw_data.url else [],
            "created_at": raw_data.collected_at.isoformat()
        }