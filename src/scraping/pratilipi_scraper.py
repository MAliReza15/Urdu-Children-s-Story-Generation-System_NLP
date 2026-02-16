from typing import List, Dict, Optional
from bs4 import BeautifulSoup
import requests
import time
import json
import re
from .base_scraper import BaseScraper


class PratilipiScraper(BaseScraper):
    """
    Scraper for Pratilipi Urdu — a large collection of user-submitted Urdu stories.
    
    Strategy:
    - Pratilipi is a SPA (Single Page App), so we try fetching the HTML
      which still contains story metadata and links
    - Visit category pages to find story URLs
    - Fetch individual story content
    """
    
    def __init__(self, config: Dict):
        super().__init__(config, 'pratilipi')
        self.base_url = self.source_config['base_url']
        self.categories = self.source_config.get('categories', [
            'shahkaar-afsaane',
            'mohabbat-ke-qisse',
        ])
        
    def get_story_urls(self) -> List[str]:
        """Get story URLs from Pratilipi category pages."""
        all_urls = []
        
        # Try API-based approach first
        api_urls = self._get_urls_from_api()
        if api_urls:
            all_urls.extend(api_urls)
        
        # Also try scraping category pages
        for category in self.categories:
            cat_url = f"{self.base_url}/categories/{category}"
            self.logger.info(f"Fetching category: {cat_url}")
            
            soup = self.fetch_page(cat_url, referer=self.base_url)
            if not soup:
                continue
            
            links = soup.find_all('a', href=True)
            for link in links:
                href = link['href']
                # Pratilipi story URLs contain /story/ or /read/
                if '/story/' in href or '/read/' in href or '/series/' in href:
                    if href.startswith('/'):
                        full_url = f"{self.base_url}{href}"
                    elif href.startswith('http'):
                        full_url = href
                    else:
                        continue
                    
                    if full_url not in all_urls:
                        all_urls.append(full_url)
        
        # Try the main page too
        soup = self.fetch_page(self.base_url)
        if soup:
            links = soup.find_all('a', href=True)
            for link in links:
                href = link['href']
                if '/story/' in href or '/read/' in href or '/series/' in href:
                    if href.startswith('/'):
                        full_url = f"{self.base_url}{href}"
                    elif href.startswith('http'):
                        full_url = href
                    else:
                        continue
                    if full_url not in all_urls:
                        all_urls.append(full_url)
        
        self.logger.info(f"Total Pratilipi story URLs: {len(all_urls)}")
        return all_urls
    
    def _get_urls_from_api(self) -> List[str]:
        """Try to get story URLs from Pratilipi's API."""
        urls = []
        try:
            # Pratilipi often has API endpoints for listing stories
            api_url = f"{self.base_url}/api/pratilipi/list"
            params = {
                'language': 'URDU',
                'listName': 'TRENDING',
                'resultCount': 50,
                'cursor': ''
            }
            
            self._random_delay()
            response = self.session.get(
                api_url, 
                params=params,
                headers=self._get_headers(referer=self.base_url),
                timeout=15
            )
            
            if response.status_code == 200:
                data = response.json()
                if 'pratilipiList' in data:
                    for story in data['pratilipiList']:
                        story_id = story.get('pratilipiId')
                        if story_id:
                            urls.append(f"{self.base_url}/story/{story_id}")
                            
        except Exception as e:
            self.logger.debug(f"API approach failed (expected): {str(e)}")
        
        return urls

    def extract_story(self, url: str) -> Optional[Dict]:
        """Extract story content from a Pratilipi story page."""
        soup = self.fetch_page(url, referer=self.base_url)
        if not soup:
            return None
        
        try:
            # Title
            title_elem = soup.select_one('h1') or soup.select_one('h2.title')
            title = title_elem.get_text(strip=True) if title_elem else ""
            
            # Content: look for the main story content div 
            content_div = (
                soup.select_one('div#pratilipiContent') or
                soup.select_one('div.pratilipi-content') or
                soup.select_one('div.story-content') or
                soup.select_one('article')
            )
            
            if not content_div:
                # Try getting all text from the page body that looks like Urdu
                body = soup.find('body')
                if body:
                    all_text = body.get_text()
                    urdu_lines = []
                    for line in all_text.split('\n'):
                        line = line.strip()
                        if line and len(line) > 20:
                            urdu_chars = len(re.findall(r'[\u0600-\u06FF]', line))
                            if urdu_chars > len(line) * 0.5:
                                urdu_lines.append(line)
                    if urdu_lines:
                        content = '\n'.join(urdu_lines)
                        slug = url.rstrip('/').split('/')[-1]
                        return {
                            'id': f"pratilipi_{slug}",
                            'title': title or slug,
                            'content': content,
                            'source': 'pratilipi',
                            'url': url,
                            'scraped_at': time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
                        }
                return None
            
            paragraphs = content_div.find_all(['p', 'div'])
            content_parts = []
            for p in paragraphs:
                text = p.get_text(strip=True)
                if text and len(text) > 10:
                    content_parts.append(text)
            
            content = '\n'.join(content_parts)
            
            if not content:
                self.logger.warning(f"No content found for {url}")
                return None
            
            slug = url.rstrip('/').split('/')[-1]
            story_id = f"pratilipi_{slug}"
            
            return {
                'id': story_id,
                'title': title or slug,
                'content': content,
                'source': 'pratilipi',
                'url': url,
                'scraped_at': time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
            }
            
        except Exception as e:
            self.logger.error(f"Error extracting story from {url}: {str(e)}")
            return None
