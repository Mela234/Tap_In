from bs4 import BeautifulSoup
from ..base_scraper import BaseScraper
from sqlalchemy.orm import Session


class RedditStyleScraper(BaseScraper):
    """Scraper for Reddit and Reddit-like forums"""
    
    def __init__(self, config):
        super().__init__()
        self.config = config
        self.name = config.get('name', 'Unknown')
        self.url = config['url']
        self.selectors = config['selectors']
        self.fields = config['fields']
        self.max_items = config.get('max_items', 25)
    
    def scrape(self, db: Session):
        """Scrape Reddit-style content"""
        
        print(f"🔍 Scraping {self.name}...")
        
        response = self.get_page(self.url)
        if not response:
            return 0
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find post containers
        posts = soup.select(self.selectors['container'])[:self.max_items]
        
        count = 0
        for post in posts:
            try:
                # Skip stickied/pinned posts if configured
                if self.config.get('skip_stickied', True):
                    if 'stickied' in post.get('class', []):
                        continue
                
                # Extract title
                title_elem = post.select_one(self.selectors['title'])
                if not title_elem:
                    continue
                
                title = title_elem.text.strip()
                
                # Extract URL
                url = None
                if 'url' in self.selectors:
                    url_elem = post.select_one(self.selectors['url'])
                    if url_elem:
                        url = url_elem.get('href', '')
                        if url and not url.startswith('http'):
                            base_url = self.config.get('base_url', 'https://old.reddit.com')
                            url = base_url + url
                
                # Extract metadata (score, comments, etc.)
                extra_data = {}
                
                if 'metadata' in self.selectors:
                    for key, selector in self.selectors['metadata'].items():
                        elem = post.select_one(selector)
                        if elem:
                            extra_data[key] = elem.text.strip()
                
                # Add post ID if available
                post_id = post.get('data-fullname', '')
                if post_id:
                    extra_data['post_id'] = post_id
                
                # Add subreddit from config
                if 'subreddit' in self.fields:
                    extra_data['subreddit'] = self.fields['subreddit']
                
                # Save to database
                self.save_to_db(
                    db=db,
                    source=self.fields['source'],
                    data_type=self.fields['data_type'],
                    content=title,
                    extra_data=extra_data,
                    url=url
                )
                
                count += 1
                
                # Show score if available
                score = extra_data.get('score', extra_data.get('upvotes', '?'))
                print(f"  ✅ {title[:60]}... ({score} ⬆️)")
                
            except Exception as e:
                print(f"  ⚠️  Error: {e}")
                continue
        
        print(f"  📊 Collected {count} items from {self.name}\n")
        return count