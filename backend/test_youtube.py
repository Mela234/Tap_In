from app.core.database import SessionLocal
from app.services.youtube_collector import YouTubeCollector

# Create database session
db = SessionLocal()

# Create collector
collector = YouTubeCollector()

# Collect trending videos + keyword searches
count = collector.collect_gen_z_trends(db)

print(f"\n✅ Successfully collected {count} videos from YouTube!")
print(f"💡 Check your data with: python check_data.py")

db.close()