from typing import List, Dict, Optional
from bs4 import BeautifulSoup
import time
from .base_scraper import BaseScraper


class BBCScraper(BaseScraper):
    """
    Scraper for BBC Urdu articles.
    
    Uses the /urdu/topics/ pages to discover article URLs,
    then extracts title and body content from each article.
    
    Note: BBC Urdu content is news/features (not fiction),
    but still valuable for building an Urdu language corpus.
    """

    def __init__(self, config: Dict):
        super().__init__(config, 'bbc_urdu')
        self.base_url = self.source_config['base_url']
        self.topics = self.source_config.get('topics', [])
        if isinstance(self.topics, str):
            self.topics = [self.topics]

    def get_story_urls(self) -> List[str]:
        """
        Get article URLs from one or more BBC Urdu topic pages.
        """
        urls = []

        for topic in self.topics:
            topic_url = f"{self.base_url}/{topic}"
            self.logger.info(f"Fetching URLs from topic: {topic_url}")
            soup = self.fetch_page(topic_url)
            if not soup:
                continue

            # BBC article links follow /urdu/articles/xxxx pattern
            for a in soup.find_all('a', href=True):
                href = a['href']
                if '/urdu/articles/' in href:
                    if href.startswith('/'):
                        href = f"https://www.bbc.com{href}"
                    if href not in urls:
                        urls.append(href)

            # Also check for /urdu/live/ links (live blogs)
            for a in soup.find_all('a', href=True):
                href = a['href']
                if '/urdu/live/' in href:
                    if href.startswith('/'):
                        href = f"https://www.bbc.com{href}"
                    if href not in urls:
                        urls.append(href)

        self.logger.info(f"Found {len(urls)} article URLs")
        return urls

    def extract_story(self, url: str) -> Optional[Dict]:
        """
        Extract BBC Urdu article content.
        
        Uses:
          - h1#content (class article-heading) for title
          - p[dir=rtl] for Urdu body paragraphs
        """
        soup = self.fetch_page(url)
        if not soup:
            return None

        try:
            # Title - BBC uses h1 with id="content" and class "article-heading"
            title_elem = soup.find('h1', id='content')
            if not title_elem:
                title_elem = soup.find('h1')
            title = title_elem.get_text(strip=True) if title_elem else ""

            # Content - BBC Urdu paragraphs have dir="rtl"
            # This filters out non-Urdu paragraphs (image captions, etc.)
            content_paragraphs = []
            for p in soup.find_all('p', attrs={'dir': 'rtl'}):
                text = p.get_text(strip=True)
                if text and len(text) > 10:  # Skip very short captions
                    content_paragraphs.append(text)

            # If no RTL paragraphs found, fall back to main tag
            if not content_paragraphs:
                main = soup.find('main')
                if main:
                    for p in main.find_all('p'):
                        text = p.get_text(strip=True)
                        if text and len(text) > 20:
                            content_paragraphs.append(text)

            content = "\n".join(content_paragraphs)

            if not title or not content:
                self.logger.warning(f"Missing title or content for {url}")
                return None

            story_id = url.split('/')[-1]

            return {
                'id': f"bbc_urdu_{story_id}",
                'title': title,
                'content': content,
                'source': 'bbc_urdu',
                'url': url,
                'scraped_at': time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
            }

        except Exception as e:
            self.logger.error(f"Error extracting story from {url}: {str(e)}")
            return None
