from typing import List, Dict, Optional
from bs4 import BeautifulSoup
import time
import re
from .base_scraper import BaseScraper


class UrduZoneScraper(BaseScraper):
    """
    Scraper for UrduZone.net — a WordPress-based Urdu stories site.
    Simple HTML structure, easy to scrape.
    """
    
    def __init__(self, config: Dict):
        super().__init__(config, 'urduzone')
        self.base_url = self.source_config['base_url']
        self.categories = self.source_config.get('categories', ['urdu-short-stories'])
        
    def get_story_urls(self) -> List[str]:
        """Get story URLs from all categories, paginated."""
        all_urls = []
        
        for category in self.categories:
            self.logger.info(f"Scraping category: {category}")
            page = 1
            consecutive_empty = 0
            
            while consecutive_empty < 2:
                if page == 1:
                    page_url = f"{self.base_url}/category/{category}/"
                else:
                    page_url = f"{self.base_url}/category/{category}/page/{page}/"
                
                self.logger.info(f"Fetching listing page {page}: {page_url}")
                soup = self.fetch_page(page_url, referer=self.base_url)
                
                if not soup:
                    consecutive_empty += 1
                    page += 1
                    continue
                
                # WordPress article links: article h2 a or h2.entry-title a
                links = soup.select('article h2 a, h2.entry-title a, .entry-title a')
                
                if not links:
                    # Fallback: try any link within article
                    links = soup.select('article a[href]')
                
                found_new = 0
                for link in links:
                    href = link.get('href', '')
                    # Filter: only story pages, not categories or tags
                    if href and self.base_url in href and '/category/' not in href and '/tag/' not in href:
                        if href not in all_urls:
                            all_urls.append(href)
                            found_new += 1
                
                self.logger.info(f"Found {found_new} new URLs on page {page}")
                
                if found_new == 0:
                    consecutive_empty += 1
                else:
                    consecutive_empty = 0
                    
                page += 1
                
                # Safety limit
                if page > 30:
                    break
        
        self.logger.info(f"Total unique story URLs found: {len(all_urls)}")
        return all_urls

    def extract_story(self, url: str) -> Optional[Dict]:
        """Extract story content from an UrduZone story page."""
        soup = self.fetch_page(url, referer=self.base_url)
        if not soup:
            return None
        
        try:
            # Title: h1.entry-title or first h1
            title_elem = soup.select_one('h1.entry-title') or soup.select_one('h1')
            title = title_elem.get_text(strip=True) if title_elem else ""
            
            # Content: div.entry-content p (WordPress standard)
            content_div = soup.select_one('div.entry-content')
            if not content_div:
                content_div = soup.select_one('article .entry-content')
            
            if not content_div:
                self.logger.warning(f"No content div found for {url}")
                return None
            
            # Get all paragraphs
            paragraphs = content_div.find_all('p')
            content_parts = []
            for p in paragraphs:
                text = p.get_text(strip=True)
                # Skip empty paragraphs and "Share this" type text
                if text and len(text) > 5 and not text.startswith('Share'):
                    content_parts.append(text)
            
            content = '\n'.join(content_parts)
            
            if not title or not content:
                self.logger.warning(f"Missing title or content for {url}")
                return None
            
            # Generate ID from URL slug
            slug = url.rstrip('/').split('/')[-1]
            story_id = f"urduzone_{slug}"
            
            return {
                'id': story_id,
                'title': title,
                'content': content,
                'source': 'urduzone',
                'url': url,
                'scraped_at': time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
            }
            
        except Exception as e:
            self.logger.error(f"Error extracting story from {url}: {str(e)}")
            return None
