import requests
from bs4 import BeautifulSoup
import time
from datetime import datetime
from sqlalchemy.orm import Session


class BaseScraper:
    """Base class for all scrapers"""
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }
        self.delay = 2  # We will delay between requests (just to be nice to servers)
    
    def get_page(self, url):
        """Fetch a webpage"""
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            time.sleep(self.delay)
            return response
        except Exception as e:
            print(f"Error fetching {url}: {e}")
            return None
    
    def save_to_db(self, db: Session, source, data_type, content, extra_data, url=None):
        """Save scraped data to database"""
        from app.models.raw_data import RawData
        
        raw_data = RawData(
            source=source,
            data_type=data_type,
            content=content,
            extra_data=extra_data,
            url=url,
            collected_at=datetime.utcnow(),
            processed=0
        )
        
        db.add(raw_data)
        db.commit()
        return raw_data.id