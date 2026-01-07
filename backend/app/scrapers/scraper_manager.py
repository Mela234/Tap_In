import yaml
from typing import List, Dict
from sqlalchemy.orm import Session
from .templates import SimpleHTMLScraper, RedditStyleScraper, NewsSiteScraper


class ScraperManager:
    """Manages all scrapers based on configuration"""
    
    def __init__(self, config_path="app/scrapers/config/scraper_config.yaml"):
        # Load configuration
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        self.scraper_types = {
            'simple_html': SimpleHTMLScraper,
            'reddit_style': RedditStyleScraper,
            'news_site': NewsSiteScraper,
        }
    
    def get_enabled_scrapers(self, priority=None) -> List[Dict]:
        """Get all enabled scrapers, optionally filtered by priority"""
        scrapers = [s for s in self.config['scrapers'] if s.get('enabled', True)]
        
        if priority:
            scrapers = [s for s in scrapers if s.get('priority') == priority]
        
        return scrapers
    
    def run_all(self, db: Session):
        """Run all enabled scrapers"""
        scrapers = self.get_enabled_scrapers()
        total_collected = 0
        
        print(f"\n{'='*80}")
        print(f"🚀 Starting TAPIN Scraper")
        print(f"📊 Running {len(scrapers)} enabled scrapers")
        print(f"{'='*80}\n")
        
        for scraper_config in scrapers:
            try:
                scraper_type = scraper_config['type']
                ScraperClass = self.scraper_types.get(scraper_type)
                
                if not ScraperClass:
                    print(f"⚠️  Unknown scraper type: {scraper_type}")
                    continue
                
                # Initialize and run the scraper
                scraper = ScraperClass(scraper_config)
                count = scraper.scrape(db)
                total_collected += count
                
            except Exception as e:
                print(f"❌ {scraper_config['name']} failed: {e}\n")
                continue
        
        return total_collected
    
    def run_priority(self, db: Session, priority: int):
        """Run only scrapers with specific priority"""
        scrapers = self.get_enabled_scrapers(priority=priority)
        
        print(f"\n{'='*80}")
        print(f"🚀 Running Priority {priority} Scrapers")
        print(f"📊 Found {len(scrapers)} scrapers")
        print(f"{'='*80}\n")
        
        total_collected = 0
        
        for scraper_config in scrapers:
            try:
                scraper_type = scraper_config['type']
                ScraperClass = self.scraper_types.get(scraper_type)
                
                if not ScraperClass:
                    continue
                
                scraper = ScraperClass(scraper_config)
                count = scraper.scrape(db)
                total_collected += count
                
            except Exception as e:
                print(f"❌ {scraper_config['name']} failed: {e}\n")
                continue
        
        return total_collected
    
    def run_single(self, db: Session, scraper_name: str):
        """Run a specific scraper by name"""
        scraper_config = None
        
        for config in self.config['scrapers']:
            if config['name'] == scraper_name:
                scraper_config = config
                break
        
        if not scraper_config:
            print(f"❌ Scraper '{scraper_name}' not found in config")
            return 0
        
        if not scraper_config.get('enabled', True):
            print(f"⚠️  Scraper '{scraper_name}' is disabled")
            return 0
        
        print(f"\n{'='*80}")
        print(f"🚀 Running Single Scraper: {scraper_name}")
        print(f"{'='*80}\n")
        
        try:
            scraper_type = scraper_config['type']
            ScraperClass = self.scraper_types.get(scraper_type)
            
            if not ScraperClass:
                print(f"❌ Unknown scraper type: {scraper_type}")
                return 0
            
            scraper = ScraperClass(scraper_config)
            count = scraper.scrape(db)
            
            return count
            
        except Exception as e:
            print(f"❌ Error: {e}")
            return 0