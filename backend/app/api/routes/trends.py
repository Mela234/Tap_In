from fastapi import APIRouter, HTTPException
from typing import Optional

router = APIRouter()

# Dummy trends data
DUMMY_TRENDS = [
    {
        "id": 1,
        "type": "video_trend",
        "title": "NPC Streaming",
        "category": "TikTok",
        "description": "Creators act like video game NPCs, repeating phrases and movements when they receive virtual gifts",
        "relevance_score": 0.95,
        "week_start": "2024-12-23",
        "week_end": "2024-12-29",
        "definition": None,
        "how_it_works": "Stream live on TikTok, repeat catchphrases when viewers send virtual gifts",
        "key_creators": [
            {"name": "Pinkydoll", "platform": "tiktok", "followers": "2.3M"}
        ],
        "signature_phrases": ["Yes yes yes!", "Ice cream so good!", "Gang gang!"],
        "example_videos": [
            {
                "url": "https://youtube.com/watch?v=xyz123",
                "title": "NPC Streaming Explained",
                "views": 2500000,
                "platform": "youtube"
            }
        ],
        "why_it_matters": "Represents a shift in how Gen Z monetizes creativity through interactive performance",
        "how_to_talk_about_it": [
            "Ask: 'Have you seen those NPC streamers?'",
            "Try: 'What do you think about this new streaming style?'"
        ],
        "context_for_adults": "Think of it like street performers - they respond to tips with specific actions",
        "source": "youtube",
        "source_links": ["https://youtube.com/watch?v=xyz123"],
        "tags": ["streaming", "monetization", "interactive", "tiktok"],
        "created_at": "2024-12-30T10:00:00Z"
    },
    {
        "id": 2,
        "type": "slang",
        "title": "Rizz",
        "category": "Slang",
        "description": "Charisma or ability to attract romantic interest",
        "relevance_score": 0.92,
        "week_start": "2024-12-23",
        "week_end": "2024-12-29",
        "definition": "Shortened from 'charisma', refers to ability to attract romantic interest",
        "pronunciation": "riz (rhymes with fizz)",
        "origin": "Popularized by streamer Kai Cenat",
        "example_usage": [
            "He's got rizz - watch how he talks to people",
            "She rizzed him up at the party",
            "No rizz = no game"
        ],
        "related_terms": ["W rizz (good)", "L rizz (bad)", "unspoken rizz"],
        "why_it_matters": "Most popular Gen Z slang term for dating appeal in 2024",
        "how_to_talk_about_it": [
            "Ask: 'What does rizz mean to you?'",
            "Try: 'I heard about this rizz thing - can you explain it?'"
        ],
        "when_to_use": "When discussing someone's charm or dating appeal",
        "when_not_to_use": "Don't use it ironically - Gen Z will know you're mocking",
        "source": "google_trends",
        "interest_score": 71.7,
        "tags": ["slang", "dating", "charisma"],
        "created_at": "2024-12-30T09:00:00Z"
    },
    {
        "id": 3,
        "type": "music",
        "title": "Brat Summer Nostalgia",
        "category": "Music",
        "description": "People reminiscing about the cultural moment around Charli XCX's album BRAT from summer 2024",
        "relevance_score": 0.88,
        "week_start": "2024-12-23",
        "week_end": "2024-12-29",
        "artist": "Charli XCX",
        "song_album": "BRAT",
        "key_songs": ["360", "Apple", "Girl, so confusing (feat. Lorde)"],
        "cultural_impact": "Influenced fashion (lime green), attitude (authenticity over perfection), and sparked conversations about female friendships",
        "why_gen_z_loves_it": "Embraces imperfection and messy emotions instead of curated perfection",
        "aesthetic": "Lime green, party girl energy, chaotic glamour",
        "peak_period": "Summer 2024",
        "why_it_matters": "Represents Gen Z's rejection of perfectionism in favor of authentic self-expression",
        "how_to_talk_about_it": [
            "Ask: 'What made brat summer so special for you?'",
            "Try: 'I noticed everyone was talking about being a brat - what did that mean?'"
        ],
        "source": "twitter",
        "source_links": ["https://twitter.com/i/web/status/123"],
        "tags": ["music", "culture", "fashion", "authenticity"],
        "created_at": "2024-12-30T08:00:00Z"
    },
    {
        "id": 4,
        "type": "meme",
        "title": "Demure",
        "category": "Memes",
        "description": "Satirical trend where people describe mundane tasks as 'very demure, very mindful'",
        "relevance_score": 0.97,
        "week_start": "2024-12-23",
        "week_end": "2024-12-29",
        "origin": "TikTok user Jools Lebron's satirical videos about workplace professionalism",
        "catchphrase": "Very demure, very mindful, very cutesy",
        "meaning": "Satirical take on workplace professionalism and feminine expectations",
        "how_its_used": [
            "Ironically describing mundane tasks as 'demure'",
            "Mocking corporate culture",
            "Self-deprecating humor about trying to be professional"
        ],
        "variations": ["Very demure, very mindful", "See how I do that? Very demure."],
        "why_it_went_viral": "Perfectly captures Gen Z's ironic relationship with professionalism",
        "why_it_matters": "Shows Gen Z's clever way of critiquing workplace culture through humor",
        "how_to_talk_about_it": [
            "Ask: 'Why did the demure trend resonate with you?'",
            "Try: 'I saw people saying demure everywhere - what's that about?'"
        ],
        "source": "tiktok",
        "source_links": ["https://tiktok.com/@joolieannie/video/123"],
        "tags": ["meme", "workplace", "satire", "humor"],
        "created_at": "2024-12-29T15:00:00Z"
    }
]

# Archive data (past weeks)
ARCHIVE_DATA = [
    {
        "week_start": "2024-12-16",
        "week_end": "2024-12-22",
        "trend_count": 4,
        "top_trends": [
            {"id": 11, "title": "Sigma Male Grindset", "category": "Memes", "relevance_score": 0.85},
            {"id": 12, "title": "Coastal Grandmother", "category": "Fashion", "relevance_score": 0.78},
            {"id": 13, "title": "No Cap", "category": "Slang", "relevance_score": 0.81}
        ]
    },
    {
        "week_start": "2024-12-09",
        "week_end": "2024-12-15",
        "trend_count": 4,
        "top_trends": [
            {"id": 21, "title": "Skibidi Toilet", "category": "Memes", "relevance_score": 0.92},
            {"id": 22, "title": "Yap", "category": "Slang", "relevance_score": 0.76},
            {"id": 23, "title": "Clean Girl Aesthetic", "category": "Fashion", "relevance_score": 0.79}
        ]
    },
    {
        "week_start": "2024-12-02",
        "week_end": "2024-12-08",
        "trend_count": 4,
        "top_trends": [
            {"id": 31, "title": "Girl Dinner", "category": "TikTok", "relevance_score": 0.84},
            {"id": 32, "title": "Bussin", "category": "Slang", "relevance_score": 0.73},
            {"id": 33, "title": "Main Character Energy", "category": "Social Issues", "relevance_score": 0.80}
        ]
    },
    {
        "week_start": "2024-11-25",
        "week_end": "2024-12-01",
        "trend_count": 4,
        "top_trends": [
            {"id": 41, "title": "Delulu", "category": "Slang", "relevance_score": 0.86},
            {"id": 42, "title": "Quiet Luxury", "category": "Fashion", "relevance_score": 0.82},
            {"id": 43, "title": "Bed Rotting", "category": "TikTok", "relevance_score": 0.77}
        ]
    }
]


@router.get("/trends/weekly")
def get_weekly_trends():
    """Get current week's trending topics"""
    return {
        "week_start": "2024-12-23",
        "week_end": "2024-12-29",
        "trends": DUMMY_TRENDS
    }


@router.get("/trends/{trend_id}")
def get_trend_by_id(trend_id: int):
    """Get detailed information about a specific trend"""
    trend = next((t for t in DUMMY_TRENDS if t["id"] == trend_id), None)
    
    if not trend:
        raise HTTPException(status_code=404, detail="Trend not found")
    
    return trend


@router.get("/trends/category/{category}")
def get_trends_by_category(category: str):
    """Get trends filtered by category"""
    filtered_trends = [t for t in DUMMY_TRENDS if t["category"].lower() == category.lower()]
    
    if not filtered_trends:
        raise HTTPException(status_code=404, detail=f"No trends found for category: {category}")
    
    return {
        "category": category,
        "trends": filtered_trends
    }


@router.get("/trends/archive")
def get_archive(page: int = 1, limit: int = 10):
    """Get archive of past weeks' trends"""
    return {
        "page": page,
        "total_pages": 1,
        "total_weeks": len(ARCHIVE_DATA),
        "archives": ARCHIVE_DATA
    }


@router.get("/trends/archive/{week_start}")
def get_archive_week(week_start: str):
    """Get trends for a specific week"""
    week = next((w for w in ARCHIVE_DATA if w["week_start"] == week_start), None)
    
    if not week:
        raise HTTPException(status_code=404, detail="Week not found")
    
    # For demo, return the top trends as full trends
    # In production, this would fetch actual trends from that week
    return {
        "week_start": week["week_start"],
        "week_end": week["week_end"],
        "trend_count": week["trend_count"],
        "trends": week["top_trends"]
    }