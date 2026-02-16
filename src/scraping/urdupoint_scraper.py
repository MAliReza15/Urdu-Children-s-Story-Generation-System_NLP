from typing import List, Dict, Optional
from bs4 import BeautifulSoup
import time
from .base_scraper import BaseScraper

class UrduPointScraper(BaseScraper):
    """Scraper for UrduPoint.com stories"""
    
    def __init__(self, config: Dict):
        super().__init__(config, 'urdupoint')
        self.base_url = self.source_config['base_url']
        self.categories = self.source_config['categories']
        self._warmup_session()
        
    def _warmup_session(self):
        """Visit the homepage first to get cookies and establish a session."""
        try:
            self.logger.info("Warming up session by visiting homepage...")
            self.session.get(
                "https://www.urdupoint.com/",
                headers=self._get_headers(),
                timeout=15
            )
            time.sleep(2)
        except Exception as e:
            self.logger.warning(f"Session warmup failed: {e}")
        
    def get_story_urls(self) -> List[str]:
        """Combine URLs from all categories."""
        all_urls = []
        for category in self.categories:
            category_url = f"{self.base_url}{category}/"
            self.logger.info(f"Fetching URLs from category: {category}")
            urls = self.get_story_urls_from_category(category_url)
            all_urls.extend(urls)
            # Be polite between categories
            time.sleep(2)
            
        return list(set(all_urls)) # Remove duplicates
    
    def get_story_urls_from_category(self, category_url: str) -> List[str]:
        """
        Extract story URLs from a category page.
        Handle pagination if present.
        """
        urls = []
        
        # Taking up to 3 pages per category
        for page in range(1, 4):
            if page == 1:
                page_url = category_url
            else:
                page_url = f"{category_url}page/{page}/"
                
            self.logger.info(f"Fetching page {page}: {page_url}")
            soup = self.fetch_page(page_url, referer=self.base_url)
            if not soup:
                continue
                
            # Selector from config: div.story-item a
            # Validating selector might be needed, but sticking to config for now.
            # Upon inspection of typical UrduPoint structure (hypothetical), 
            # might need adjustment.
            # Using selector from config:
            selector = self.source_config['selectors']['story_list']
            links = soup.select(selector)
            
            for link in links:
                href = link.get('href')
                if href:
                    # Resolve relative URLs if necessary
                    if not href.startswith('http'):
                        if href.startswith('/'):
                            href = "https://www.urdupoint.com" + href
                        else:
                            href = category_url + href
                    urls.append(href)
            
            # If no links found, stop pagination
            if not links:
                break
                
        return urls

    def extract_story(self, url: str) -> Optional[Dict]:
        """
        Extract story from UrduPoint page.
        """
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
                
            # Metadata
            # Try to find author/date if available, otherwise generic
            story_id = url.split('/')[-1].replace('.html', '')
            
            return {
                'id': f"urdupoint_{story_id}",
                'title': title,
                'content': content,
                'source': 'urdupoint',
                'url': url,
                'scraped_at': time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
            }
            
        except Exception as e:
            self.logger.error(f"Error extracting story from {url}: {str(e)}")
            return None
