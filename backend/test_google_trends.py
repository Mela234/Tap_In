# from app.core.database import SessionLocal
# from app.services.google_trends import GoogleTrendsCollector

# # Create database session
# db = SessionLocal()

# # Create collector and run it
# collector = GoogleTrendsCollector()
# count = collector.collect_trending_searches(db)

# print(f"\n✅ Collected {count} trending searches from Google Trends!")

# db.close()
from app.core.database import SessionLocal
from app.services.google_trends import GoogleTrendsCollector

# Create database session
db = SessionLocal()

# Create collector and run it
collector = GoogleTrendsCollector()

# Custom keywords to track
gen_z_keywords = [
    "brat summer",
    "demure",
    "skibidi",
    "rizz",
    "no cap"
]

count = collector.collect_trending_topics(db, keywords=gen_z_keywords)

print(f"\n✅ Collected data for {count} keywords from Google Trends!")

db.close()