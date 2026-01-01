import os
from pytrends.request import TrendReq
from datetime import datetime
from sqlalchemy.orm import Session
import time


class GoogleTrendsCollector:
    """Collects trending data from Google Trends"""
    
    def __init__(self):
        # Initialize pytrends with timeout
        self.pytrends = TrendReq(hl='en-US', tz=360, timeout=(10, 25))
    
    def collect_trending_topics(self, db: Session, keywords=None):
        """
        Fetch interest data for Gen Z related keywords
        """
        from app.models.raw_data import RawData
        
        # Default Gen Z keywords to track
        if keywords is None:
            keywords = [
                "tiktok trends",
                "gen z slang",
                "viral challenge",
                "trending dance",
                "new meme"
            ]
        
        try:
            count = 0
            
            for keyword in keywords:
                try:
 
                    self.pytrends.build_payload([keyword], timeframe='now 7-d')
                    
                    # Get interest over time
                    interest_df = self.pytrends.interest_over_time()
                    
                    if not interest_df.empty:
                        # Get average interest score
                        avg_interest = interest_df[keyword].mean()
                        
                        # Store in database
                        raw_data = RawData(
                            source="google_trends",
                            data_type="keyword_interest",
                            content=keyword,
                            extra_data={
                                "avg_interest_score": float(avg_interest),
                                "timeframe": "7 days"
                            },
                            url=None,
                            collected_at=datetime.utcnow(),
                            processed=0
                        )
                        db.add(raw_data)
                        count += 1

                    # Sleep to avoid rate limiting
                    time.sleep(2)
                    
                except Exception as e:
                    print(f"⚠️  Error with keyword '{keyword}': {e}")
                    continue
            
            db.commit()
            return count
            
        except Exception as e:
            print(f"❌ Error collecting Google Trends: {e}")
            db.rollback()
            return 0