import os
import tweepy
from datetime import datetime
from sqlalchemy.orm import Session


class TwitterCollector:
    """Collects trending topics and tweets from Twitter/X"""
    
    def __init__(self):
        # Initialize Twitter API client with Bearer Token
        bearer_token = os.getenv("TWITTER_BEARER_TOKEN")
        self.client = tweepy.Client(bearer_token=bearer_token)
        
    def get_trending_topics(self, woeid=23424977):
        """
        Get trending topics for a location
        woeid: 23424977 = United States (default)
        Other examples: 1 = Worldwide, 2459115 = New York
        
        NOTE: Trending topics endpoint requires API v1.1 and elevated access
        For Free/Basic tier, we'll use a workaround with search
        """
        # Free tier limitation: Can't access trends directly
        # Instead, we'll use known Gen Z keywords as proxy
        return [
            "brat summer",
            "demure", 
            "rizz",
            "skibidi",
            "sigma",
            "gyatt",
            "no cap",
            "bussin",
            "slay"
        ]
    
    def collect_tweets_for_trend(self, db: Session, keyword, max_results=10):
        """
        Collect tweets for a specific trending keyword
        Free tier: 100 tweets/month total
        """
        from app.models.raw_data import RawData
        
        try:
            # Search recent tweets (last 7 days)
            tweets = self.client.search_recent_tweets(
                query=f"{keyword} -is:retweet lang:en",  # Exclude retweets, English only
                max_results=max_results,
                tweet_fields=['created_at', 'public_metrics', 'author_id']
            )
            
            if not tweets.data:
                print(f"  ⚠️  No tweets found for: {keyword}")
                return 0
            
            count = 0
            for tweet in tweets.data:
                # Store in database
                raw_data = RawData(
                    source="twitter",
                    data_type="tweet",
                    content=tweet.text,
                    extra_data={
                        "keyword": keyword,
                        "tweet_id": tweet.id,
                        "author_id": tweet.author_id,
                        "created_at": str(tweet.created_at),
                        "likes": tweet.public_metrics['like_count'],
                        "retweets": tweet.public_metrics['retweet_count'],
                        "replies": tweet.public_metrics['reply_count']
                    },
                    url=f"https://twitter.com/i/web/status/{tweet.id}",
                    collected_at=datetime.utcnow(),
                    processed=0
                )
                
                db.add(raw_data)
                count += 1
            
            db.commit()
            print(f"  ✅ Collected {count} tweets for: {keyword}")
            return count
            
        except tweepy.TooManyRequests as e:
            print(f"  ❌ Rate limit hit for '{keyword}'")
            return 0
        except Exception as e:
            print(f"  ❌ Error collecting tweets for '{keyword}': {e}")
            db.rollback()
            return 0
    
    def collect_all_trends(self, db: Session, tweets_per_keyword=10):
        """
        Collect tweets for all trending keywords
        
        Strategy for Free tier (100 tweets/month):
        - 5 keywords × 10 tweets = 50 tweets (leaves buffer)
        """
        print("\n🐦 Starting Twitter collection...")
        
        # Get trending topics (or use predefined Gen Z keywords)
        keywords = self.get_trending_topics()
        
        # Limit to 5 keywords to stay under free tier limit
        keywords = keywords[:5]
        
        print(f"📊 Tracking {len(keywords)} keywords: {', '.join(keywords)}\n")
        
        total_collected = 0
        
        for keyword in keywords:
            count = self.collect_tweets_for_trend(db, keyword, max_results=tweets_per_keyword)
            total_collected += count
        
        print(f"\n🎉 Total: Collected {total_collected} tweets from Twitter!")
        print(f"📊 Free tier usage: {total_collected}/100 tweets this month")
        
        return total_collected