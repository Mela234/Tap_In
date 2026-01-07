from app.core.database import SessionLocal
from app.scrapers.scraper_manager import ScraperManager


def main():
    """Run scrapers"""
    
    db = SessionLocal()
    
    try:
        manager = ScraperManager()
        
        # Show all available scrapers
        print(f"\n{'='*80}")
        print(f"📋 AVAILABLE SCRAPERS")
        print(f"{'='*80}")
        
        for idx, config in enumerate(manager.config['scrapers'], 1):
            status = "✅" if config.get('enabled', True) else "❌"
            print(f"{idx}. {status} {config['name']}")
            print(f"   Type: {config['type']} | Priority: {config.get('priority', 'N/A')}")
            print()
        
        print(f"{'='*80}\n")
        
        # TEST A SPECIFIC SCRAPER HERE
        scraper_name = "BuzzFeed Trending"  # ← CHANGE THIS TO TEST DIFFERENT ONES
        
        # Show which one we're testing
        for config in manager.config['scrapers']:
            if config['name'] == scraper_name:
                print(f"🧪 TESTING: {config['name']}")
                print(f"📦 Using template: {config['type']}")
                print(f"🌐 URL: {config['url']}\n")
                break
        
        # Run it
        count = manager.run_single(db, scraper_name)
        
        print(f"\n{'='*80}")
        print(f"✅ TEST COMPLETE!")
        print(f"📊 Collected {count} items")
        print(f"{'='*80}\n")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        db.close()


if __name__ == "__main__":
    main()