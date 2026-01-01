from app.core.database import SessionLocal
from app.services.twitter_collector import TwitterCollector

# Create database session
db = SessionLocal()

# Create collector
collector = TwitterCollector()

# Collect tweets (10 tweets per keyword × 5 keywords = 50 tweets)
count = collector.collect_all_trends(db, tweets_per_keyword=10)

print(f"\n✅ Successfully collected {count} tweets!")
print(f"💡 Tip: Check your data with: python check_data.py")

db.close()