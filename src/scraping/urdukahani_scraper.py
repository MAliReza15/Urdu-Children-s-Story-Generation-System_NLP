from typing import List, Dict, Optional
from bs4 import BeautifulSoup
import time
from .base_scraper import BaseScraper

class UrduKahaniScraper(BaseScraper):
    """Scraper for UrduKahani.com"""
    
    def __init__(self, config: Dict):
        super().__init__(config, 'urdukahani')
        self.base_url = self.source_config['base_url']
        
    def get_story_urls(self) -> List[str]:
        """
        Navigate all categories.
        """
        # Iterate over known categories or just scrape the main feed
        # Assuming categories are listed on home page or we can iterate pages
        urls = []
        
        # Taking top 5 pages from home for simplicity
        for page in range(1, 6):
            if page == 1:
                page_url = self.base_url
            else:
                page_url = f"{self.base_url}/page/{page}/"
                
            self.logger.info(f"Fetching page {page}: {page_url}")
            soup = self.fetch_page(page_url)
            if not soup:
                continue
                
            selector = self.source_config['selectors']['story_list']
            links = soup.select(selector)
            
            for link in links:
                href = link.get('href')
                if href:
                    urls.append(href)
            
            if not links:
                break
                
        return list(set(urls))
    
    def extract_story(self, url: str) -> Optional[Dict]:
        """Extract story from UrduKahani page."""
        soup = self.fetch_page(url)
        if not soup:
            return None
        
        try:
            selectors = self.source_config['selectors']
            
            # Title
            title_elem = soup.select_one(selectors['title'])
            title = title_elem.get_text(strip=True) if title_elem else ""
            
            # Content
            content_elems = soup.select(selectors['content'])
            content = "\n".join([p.get_text(strip=True) for p in content_elems])
            
            if not title or not content:
                self.logger.warning(f"Missing title or content for {url}")
                return None
            
            story_id = url.split('/')[-1].replace('.html', '')
            
            return {
                'id': f"urdukahani_{story_id}",
                'title': title,
                'content': content,
                'source': 'urdukahani',
                'url': url,
                'scraped_at': time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
            }
            
        except Exception as e:
            self.logger.error(f"Error extracting story from {url}: {str(e)}")
            return None
