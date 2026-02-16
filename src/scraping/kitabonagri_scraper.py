from typing import List, Dict, Optional
from bs4 import BeautifulSoup
import time
from .base_scraper import BaseScraper

class KitabNagriScraper(BaseScraper):
    """Scraper for KitabONagri.com"""
    
    def __init__(self, config: Dict):
        super().__init__(config, 'kitabonagri')
        self.base_url = self.source_config['base_url']
        
    def get_story_urls(self) -> List[str]:
        """
        Navigate book/story sections.
        """
        urls = []
        # Example URL structure: https://www.kitabonagri.com/category/romantic-novels/
        # Or specific story sections.
        # Starting with a known category or search page.
        # Since config doesn't specify categories for KitabNagri, we'll assume a default or main page.
        # Let's try the base URL and look for "Novel" or "Story" links.
        
        # A probable better approach for KitabNagri is to iterate through a "Novels" list if available.
        # For now, let's assume we scrape the main page or a specific verified category.
        target_url = f"{self.base_url}/category/urdu-novels/" # Heuristic
        
        self.logger.info(f"Fetching URLs from: {target_url}")
        soup = self.fetch_page(target_url)
        if not soup:
            return []
            
        selector = self.source_config['selectors']['story_list']
        links = soup.select(selector)
        
        for link in links:
            href = link.get('href')
            if href:
                urls.append(href)
                
        return list(set(urls))
    
    def extract_story(self, url: str) -> Optional[Dict]:
        """Extract story from HTML."""
        soup = self.fetch_page(url)
        if not soup:
            return None
        
        try:
            selectors = self.source_config['selectors']
            
            # Title
            title_elem = soup.select_one(selectors['title'])
            title = title_elem.get_text(strip=True) if title_elem else ""
            
            # Content
            # KitabNagri might splits content into pages or have a "Read Online" button.
            # If "Read Online" is a separate link, we need to follow it.
            # For this implementation, we assume the content selector points to the content 
            # or we need to find the "Read Online" link.
            
            content_elem = soup.select_one(selectors['content'])
            
            # Check if there is a "Read Online" link if content is empty
            if not content_elem or not content_elem.get_text(strip=True):
                read_link = soup.find('a', string=lambda t: t and "Read Online" in t)
                if read_link:
                    read_url = read_link.get('href')
                    self.logger.info(f"Following 'Read Online' link: {read_url}")
                    soup = self.fetch_page(read_url)
                    if soup:
                        content_elem = soup.select_one(selectors['content'])
            
            content = content_elem.get_text(strip=True) if content_elem else ""
            
            if not title or not content:
                self.logger.warning(f"Missing title or content for {url}")
                return None
            
            story_id = url.split('/')[-1].replace('.html', '')
            
            return {
                'id': f"kitabonagri_{story_id}",
                'title': title,
                'content': content,
                'source': 'kitabonagri',
                'url': url,
                'scraped_at': time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
            }
            
        except Exception as e:
            self.logger.error(f"Error extracting story from {url}: {str(e)}")
            return None
