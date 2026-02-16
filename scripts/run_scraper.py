import argparse
import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from src.scraping.scraper_manager import ScraperManager

def main():
    parser = argparse.ArgumentParser(description="Run Urdu Story Scrapers")
    parser.add_argument('--config', type=str, default='config/scraping_config.yaml', help='Path to config file')
    parser.add_argument('--source', type=str, help='Run specific scraper (urdupoint, rekhta, bbc_urdu)')
    parser.add_argument('--all', action='store_true', help='Run all enabled scrapers')
    parser.add_argument('--test', action='store_true', help='Test mode: scrape only 1 story per source')
    
    args = parser.parse_args()
    
    manager = ScraperManager(args.config)
    
    if args.all:
        sources = ['rekhta', 'bbc_urdu', 'urdupoint']
    elif args.source:
        sources = [args.source]
    else:
        print("Please specify --all or --source <name>")
        print("Available sources: urdupoint, rekhta, bbc_urdu")
        return
        
    for source in sources:
        manager.register_scraper(source)
        
    results = manager.run_all_scrapers(test_mode=args.test)
    
    print("\n" + "="*50)
    print("SCRAPING RESULTS:")
    print("="*50)
    for source, count in results.items():
        print(f"  {source}: {count} stories")
    print("="*50)

if __name__ == "__main__":
    main()
