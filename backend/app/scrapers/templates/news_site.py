from bs4 import BeautifulSoup
from ..base_scraper import BaseScraper
from sqlalchemy.orm import Session


class NewsSiteScraper(BaseScraper):
    """Scraper for news sites and blogs"""
    
    def __init__(self, config):
        super().__init__()
        self.config = config
        self.name = config['name']
        self.url = config['url']
        self.selectors = config['selectors']
        self.fields = config['fields']
        self.max_items = config.get('max_items', 15)
    
    def scrape(self, db: Session):
        """Scrape news articles"""
        
        print(f"🔍 Scraping {self.name}...")
        
        response = self.get_page(self.url)
        if not response:
            return 0
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find article containers
        articles = soup.select(self.selectors['container'])[:self.max_items]
        
        count = 0
        for article in articles:
            try:
                title_elem = article.select_one(self.selectors['title'])
                if not title_elem:
                    continue
                
                title = title_elem.text.strip()
                
                content = title
                if 'description' in self.selectors:
                    desc_elem = article.select_one(self.selectors['description'])
                    if desc_elem:
                        content = f"{title}\n\n{desc_elem.text.strip()}"
                
                url = None
                if 'url' in self.selectors:
                    url_elem = article.select_one(self.selectors['url'])
                    if url_elem:
                        url = url_elem.get('href', '')
                        if url and not url.startswith('http'):
                            base_url = self.config.get('base_url', self.url)
                            url = base_url.rstrip('/') + '/' + url.lstrip('/')
                
                # Extract metadata
                extra_data = {}
                if 'metadata' in self.selectors:
                    for key, selector in self.selectors['metadata'].items():
                        elem = article.select_one(selector)
                        if elem:
                            extra_data[key] = elem.text.strip()
                
                self.save_to_db(
                    db=db,
                    source=self.fields['source'],
                    data_type=self.fields['data_type'],
                    content=content,
                    extra_data=extra_data,
                    url=url
                )
                
                count += 1
                print(f"  ✅ {title[:60]}...")
                
            except Exception as e:
                print(f"  ⚠️  Error: {e}")
                continue
        
        print(f"  📊 Collected {count} items from {self.name}\n")
        return count