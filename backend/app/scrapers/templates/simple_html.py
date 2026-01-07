from bs4 import BeautifulSoup
from ..base_scraper import BaseScraper
from sqlalchemy.orm import Session


class SimpleHTMLScraper(BaseScraper):
    """Generic scraper for simple HTML sites"""
    
    def __init__(self, config):
        super().__init__()
        self.config = config
        self.name = config.get('name', 'Unknown')  
        self.url = config['url']
        self.selectors = config['selectors']
        self.fields = config['fields']
        self.max_items = config.get('max_items', 20)
    
    def scrape(self, db: Session):
        """Scrape using configuration"""
        
        print(f"🔍 Scraping {self.name}...")
        
        response = self.get_page(self.url)
        if not response:
            return 0
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # DEBUG: Print what we're looking for
        print(f"  🔎 Looking for container: {self.selectors['container']}")
        
        containers = soup.select(self.selectors['container'])[:self.max_items]
        
        print(f"  📦 Found {len(containers)} containers")
        
        if len(containers) == 0:
            print(f"  ⚠️  No containers found! Trying to find ANY div on page...")
            all_divs = soup.find_all('div', limit=5)
            for i, div in enumerate(all_divs):
                print(f"  Sample div {i}: {str(div)[:150]}...")
        
        count = 0
        for idx, container in enumerate(containers):
            try:
                print(f"\n  🔍 Container {idx+1} HTML: {str(container)[:300]}...")

                print(f"  🎯 Looking for title with selector: {self.selectors['title']}")
                title_elem = container.select_one(self.selectors['title'])
                
                print(f"  📝 Title element: {title_elem}")
                
                if not title_elem:
                    print(f"  ⚠️  No title element found in this container!")
                    continue
                
                title = title_elem.text.strip()
                print(f"  ✅ Title extracted: {title}")
                
                # Extract content if configured
                content = title
                if 'content' in self.selectors:
                    content_elem = container.select_one(self.selectors['content'])
                    if content_elem:
                        content_text = content_elem.text.strip()
                        content = f"{title}\n\n{content_text}"
                        print(f"  📄 Content: {content_text[:100]}...")
                
                # Extract extra metadata and save the word!
                extra_data = {
                    "word": title,  # Save the title as the word
                    "definition": ""  # Will be filled below
                }
                
                if 'content' in self.selectors:
                    content_elem = container.select_one(self.selectors['content'])
                    if content_elem:
                        extra_data["definition"] = content_elem.text.strip()
                
                if 'metadata' in self.selectors:
                    for key, selector in self.selectors['metadata'].items():
                        elem = container.select_one(selector)
                        if elem:
                            extra_data[key] = elem.text.strip()
                            print(f"  📊 Metadata {key}: {elem.text.strip()[:50]}...")
                
                # Get URL if configured
                url = self.url #default url
                if 'url' in self.selectors:
                    url_elem = container.select_one(self.selectors['url'])
                    if url_elem:
                        url = url_elem.get('href', '')
                        if url and not url.startswith('http'):
                            base_url = self.config.get('base_url', self.url)
                            url = base_url + url
                
                self.save_to_db(
                    db=db,
                    source=self.fields['source'],
                    data_type=self.fields['data_type'],
                    content=content,
                    extra_data=extra_data,
                    url=url if url else self.url
                )
                
                count += 1
                print(f"  ✅ Saved: {title[:60]}...\n")
                
            except Exception as e:
                print(f"  ❌ Error in container {idx+1}: {e}")
                import traceback
                traceback.print_exc()
                continue
        
        print(f"  📊 Collected {count} items from {self.name}\n")
        return count