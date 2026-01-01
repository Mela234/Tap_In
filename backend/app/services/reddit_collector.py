import os
import praw
from datetime import datetime
from sqlalchemy.orm import Session


class RedditCollector:
    """Collects trending posts from Gen Z subreddits"""
    
    def __init__(self):
        # Initialize Reddit API client
        self.reddit = praw.Reddit(
            client_id=os.getenv("REDDIT_CLIENT_ID"),
            client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
            user_agent="TAPIN Trend Collector v1.0"
        )
        
        # Gen Z focused subreddits
        self.target_subreddits = [
            "GenZ",
            "teenagers", 
            "TikTokCringe",
            "OutOfTheLoop",
            "ExplainTheJoke"
        ]
    
    def collect_hot_posts(self, db: Session, limit=25):
        """
        Fetch hot posts from Gen Z subreddits
        """
        from app.models.raw_data import RawData
        
        total_collected = 0
        
        for subreddit_name in self.target_subreddits:
            try:
                print(f"\n📱 Fetching from r/{subreddit_name}...")
                
                subreddit = self.reddit.subreddit(subreddit_name)
                
                # Get hot posts
                for post in subreddit.hot(limit=limit):
                    # Skip stickied posts (announcements)
                    if post.stickied:
                        continue
                    
                    # Combine title and body text
                    content = f"{post.title}\n\n{post.selftext}" if post.selftext else post.title
                    
                    # Store in database
                    raw_data = RawData(
                        source="reddit",
                        data_type="post",
                        content=content,
                        extra_data={
                            "subreddit": subreddit_name,
                            "upvotes": post.score,
                            "comments": post.num_comments,
                            "author": str(post.author),
                            "created_utc": post.created_utc
                        },
                        url=f"https://reddit.com{post.permalink}",
                        collected_at=datetime.utcnow(),
                        processed=0
                    )
                    
                    db.add(raw_data)
                    total_collected += 1
                
                print(f"  ✅ Collected {limit} posts from r/{subreddit_name}")
                
            except Exception as e:
                print(f"  ❌ Error with r/{subreddit_name}: {e}")
                continue
        
        db.commit()
        print(f"\n🎉 Total: Collected {total_collected} Reddit posts!")
        return total_collected