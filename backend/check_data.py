from app.core.database import SessionLocal
from app.models.raw_data import RawData
from datetime import datetime

db = SessionLocal()

print("\n" + "="*80)
print("📊 TAPIN DATABASE CONTENTS")
print("="*80)

# Get all raw data
all_data = db.query(RawData).all()

print(f"\n📈 Total items in database: {len(all_data)}\n")

# Group by source
sources = {}
for item in all_data:
    if item.source not in sources:
        sources[item.source] = []
    sources[item.source].append(item)

# Display each source
for source, items in sources.items():
    print("\n" + "-"*80)
    print(f"📁 {source.upper()}: {len(items)} items")
    print("-"*80)
    
    for i, item in enumerate(items, 1):
        print(f"\n[{i}] ID: {item.id} | Collected: {item.collected_at.strftime('%Y-%m-%d %H:%M')}")
        
        if source == "urban_dictionary":
            word = item.extra_data.get('word', 'Unknown')
            definition = item.extra_data.get('definition', '')
            example = item.extra_data.get('example', '')
            upvotes = item.extra_data.get('upvotes', '0')
            
            print(f"    Word: {word}")
            print(f"    Definition: {definition[:100]}...")
            if example:
                print(f"    Example: {example[:100]}...")
            print(f"    Upvotes: {upvotes}")
            print(f"    URL: {item.url}")
            
        elif source == "google_trends":
            score = item.extra_data.get('avg_interest_score', 0)
            print(f"    Keyword: {item.content}")
            print(f"    Interest Score: {score:.1f}/100")
            
        elif source == "twitter":
            keyword = item.extra_data.get('keyword', 'unknown')
            likes = item.extra_data.get('likes', 0)
            retweets = item.extra_data.get('retweets', 0)
            print(f"    Keyword: {keyword}")
            print(f"    Tweet: {item.content[:100]}...")
            print(f"    Engagement: {likes} ❤️  | {retweets} 🔄")
            print(f"    URL: {item.url}")
            
        elif source == "youtube":
            video_id = item.extra_data.get('video_id', '')
            channel = item.extra_data.get('channel_title', 'Unknown')
            views = item.extra_data.get('views', 0)
            likes = item.extra_data.get('likes', 0)
            
            # Extract title (first line of content)
            title = item.content.split('\n')[0]
            
            print(f"    Title: {title[:80]}...")
            print(f"    Channel: {channel}")
            print(f"    Stats: {views:,} views | {likes:,} likes")
            print(f"    URL: {item.url}")
            
        elif source == "reddit":
            subreddit = item.extra_data.get('subreddit', 'unknown')
            upvotes = item.extra_data.get('score', item.extra_data.get('upvotes', 0))
            comments = item.extra_data.get('comments', 0)
            
            # Extract title
            title = item.content.split('\n')[0] if '\n' in item.content else item.content
            
            print(f"    Subreddit: r/{subreddit}")
            print(f"    Title: {title[:80]}...")
            print(f"    Engagement: {upvotes} ⬆️  | {comments} 💬")
            print(f"    URL: {item.url}")
        
        elif source == "knowyourmeme":
            meme_name = item.extra_data.get('meme_name', 'Unknown')
            description = item.extra_data.get('description', '')
            
            print(f"    Meme: {meme_name}")
            print(f"    Description: {description[:100]}...")
            print(f"    URL: {item.url}")
        
        elif source in ["buzzfeed", "complex", "thecut", "refinery29"]:
            # News sites
            title = item.content.split('\n')[0] if '\n' in item.content else item.content
            print(f"    Title: {title[:80]}...")
            print(f"    URL: {item.url}")
        
        else:
            # Generic display
            print(f"    Content: {item.content[:100]}...")
            if item.url:
                print(f"    URL: {item.url}")
        
        print(f"    Processed: {'✅ Yes' if item.processed else '❌ No'}")

print("\n" + "="*80)
print("📊 SUMMARY BY SOURCE")
print("="*80)

for source, items in sources.items():
    print(f"{source.upper()}: {len(items)} items")

print("\n" + "="*80 + "\n")

db.close()