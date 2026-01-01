import os
from googleapiclient.discovery import build
from datetime import datetime, timedelta
from sqlalchemy.orm import Session


class YouTubeCollector:
    """Collects trending videos from YouTube"""
    
    def __init__(self):
        # Initialize YouTube API client
        api_key = os.getenv("YOUTUBE_API_KEY")
        self.youtube = build('youtube', 'v3', developerKey=api_key)
    
    def get_trending_videos(self, db: Session, region_code='US', max_results=25):
        """
        Get videos from YouTube's official trending page
        """
        from app.models.raw_data import RawData
        
        try:
            print(f"\n📺 Fetching {max_results} trending videos from YouTube...")
            
            # Get trending videos
            request = self.youtube.videos().list(
                part='snippet,statistics',
                chart='mostPopular',
                regionCode=region_code,
                maxResults=max_results,
                videoCategoryId='24'  # Entertainment category (most Gen Z content)
            )
            response = request.execute()
            
            count = 0
            for video in response.get('items', []):
                snippet = video['snippet']
                stats = video['statistics']
                
                # Store in database
                raw_data = RawData(
                    source="youtube",
                    data_type="video",
                    content=f"{snippet['title']}\n\n{snippet.get('description', '')[:500]}",  # Limit description
                    extra_data={
                        "video_id": video['id'],
                        "channel_title": snippet['channelTitle'],
                        "published_at": snippet['publishedAt'],
                        "category_id": snippet.get('categoryId'),
                        "views": int(stats.get('viewCount', 0)),
                        "likes": int(stats.get('likeCount', 0)),
                        "comments": int(stats.get('commentCount', 0))
                    },
                    url=f"https://www.youtube.com/watch?v={video['id']}",
                    collected_at=datetime.utcnow(),
                    processed=0
                )
                
                db.add(raw_data)
                count += 1
                
                views = int(stats.get('viewCount', 0))
                print(f"  ✅ {snippet['title'][:60]}... ({views:,} views)")
            
            db.commit()
            print(f"\n🎉 Collected {count} trending videos from YouTube!")
            return count
            
        except Exception as e:
            print(f"❌ Error collecting YouTube videos: {e}")
            db.rollback()
            return 0
    
    def search_recent_videos(self, db: Session, keyword, max_results=10):
        """
        Search for recent videos by keyword (uploaded in last 7 days)
        """
        from app.models.raw_data import RawData
        
        try:
            # Calculate date 7 days ago
            week_ago = (datetime.utcnow() - timedelta(days=7)).strftime('%Y-%m-%dT%H:%M:%SZ')
            
            # Search for videos
            request = self.youtube.search().list(
                part='snippet',
                q=keyword,
                type='video',
                publishedAfter=week_ago,
                order='viewCount',  # Sort by view count
                maxResults=max_results,
                relevanceLanguage='en'
            )
            response = request.execute()
            
            if not response.get('items'):
                print(f"  ⚠️  No videos found for: {keyword}")
                return 0
            
            count = 0
            for item in response.get('items', []):
                snippet = item['snippet']
                video_id = item['id']['videoId']
                
                # Get video statistics (requires separate API call)
                stats_request = self.youtube.videos().list(
                    part='statistics',
                    id=video_id
                )
                stats_response = stats_request.execute()
                stats = stats_response['items'][0]['statistics'] if stats_response.get('items') else {}
                
                # Store in database
                raw_data = RawData(
                    source="youtube",
                    data_type="video",
                    content=f"{snippet['title']}\n\n{snippet.get('description', '')[:500]}",
                    extra_data={
                        "video_id": video_id,
                        "channel_title": snippet['channelTitle'],
                        "published_at": snippet['publishedAt'],
                        "keyword": keyword,
                        "views": int(stats.get('viewCount', 0)),
                        "likes": int(stats.get('likeCount', 0)),
                        "comments": int(stats.get('commentCount', 0))
                    },
                    url=f"https://www.youtube.com/watch?v={video_id}",
                    collected_at=datetime.utcnow(),
                    processed=0
                )
                
                db.add(raw_data)
                count += 1
            
            db.commit()
            print(f"  ✅ Collected {count} videos for: {keyword}")
            return count
            
        except Exception as e:
            print(f"  ❌ Error searching YouTube for '{keyword}': {e}")
            db.rollback()
            return 0
    
    def collect_gen_z_trends(self, db: Session):
        """
        Collect videos using multiple strategies:
        1. Trending videos (Entertainment category)
        2. Search for Gen Z keywords
        """
        print("\n📺 Starting YouTube collection...")
        
        total = 0
        
        # Strategy 1: Get trending videos
        total += self.get_trending_videos(db, max_results=20)
        
        # Strategy 2: Search for Gen Z keywords
        gen_z_keywords = ["gen z", "tiktok trend", "viral dance", "new slang 2024"]
        
        print(f"\n🔍 Searching for Gen Z keywords...")
        for keyword in gen_z_keywords:
            count = self.search_recent_videos(db, keyword, max_results=5)
            total += count
        
        print(f"\n🎉 Total: Collected {total} videos from YouTube!")
        return total