from typing import List, Dict, Optional
from bs4 import BeautifulSoup
import time
import re
from .base_scraper import BaseScraper


class RekhtaScraper(BaseScraper):
    """
    Scraper for Rekhta.org Urdu short stories.
    
    Uses plain HTTP requests (no Selenium needed).
    Appends ?lang=ur to get Urdu script content.
    
    Flow:
      1. Fetch /stories listing → collect author page URLs
      2. For each author page → collect individual story URLs
      3. For each story URL → extract title + content in Urdu
    """

    def __init__(self, config: Dict):
        super().__init__(config, 'rekhta')
        self.base_url = self.source_config['base_url'].rstrip('/')

    def get_story_urls(self) -> List[str]:
        """
        Collect story URLs by:
          1. Scraping the /stories page for author links
          2. Visiting each author's stories page to get individual story URLs
        """
        author_urls = self._get_author_urls()
        self.logger.info(f"Found {len(author_urls)} author pages")

        all_story_urls = []
        target = self.source_config.get('target_stories', 120)

        for i, author_url in enumerate(author_urls):
            if len(all_story_urls) >= target * 2:
                # Collect more than target to have buffer after validation
                break

            self.logger.info(f"Fetching stories from author {i+1}/{len(author_urls)}: {author_url}")
            story_urls = self._get_stories_from_author(author_url)
            all_story_urls.extend(story_urls)
            time.sleep(1)  # Be polite

        unique_urls = list(dict.fromkeys(all_story_urls))  # Deduplicate, preserve order
        self.logger.info(f"Collected {len(unique_urls)} unique story URLs")
        return unique_urls

    def _get_author_urls(self) -> List[str]:
        """Scrape /stories page for author/storywriter links."""
        urls = []
        listing_url = f"{self.base_url}/stories"

        self.logger.info(f"Fetching author listing from: {listing_url}")
        soup = self.fetch_page(listing_url)
        if not soup:
            return urls

        for a in soup.find_all('a', href=True):
            href = a['href']
            if ('/authors/' in href or '/storywriter/' in href) and '/stories' in href:
                # Make absolute URL
                if href.startswith('/'):
                    href = f"{self.base_url}{href}"
                if href not in urls:
                    urls.append(href)

        return urls

    def _get_stories_from_author(self, author_url: str) -> List[str]:
        """Get individual story URLs from an author's stories page."""
        soup = self.fetch_page(author_url)
        if not soup:
            return []

        story_urls = []
        for a in soup.find_all('a', href=True):
            href = a['href']
            # Story URLs look like /stories/story-name-author-stories
            if '/stories/' in href and href != '/stories' and href != '/stories/':
                # Skip author listing links
                path = href.rstrip('/')
                if path.count('/') >= 2 and 'stories' != path.split('/')[-1]:
                    if href.startswith('/'):
                        href = f"{self.base_url}{href}"
                    # Append ?lang=ur for Urdu content
                    if '?lang=ur' not in href:
                        href = href + '?lang=ur'
                    if href not in story_urls:
                        story_urls.append(href)

        return story_urls

    def extract_story(self, url: str) -> Optional[Dict]:
        """
        Extract story content from a Rekhta story page.
        
        Uses:
          - h1 for title
          - div.poemPageContentBody for content
          - Appends ?lang=ur if not already present
        """
        # Ensure we're requesting Urdu version
        if '?lang=ur' not in url and '&lang=ur' not in url:
            url = url + ('&lang=ur' if '?' in url else '?lang=ur')

        soup = self.fetch_page(url)
        if not soup:
            return None

        try:
            # Title from h1
            title_elem = soup.find('h1')
            title = title_elem.get_text(strip=True) if title_elem else ""

            # Content from div.poemPageContentBody
            content_div = soup.select_one('div.poemPageContentBody')
            if not content_div:
                self.logger.warning(f"No content div found for {url}")
                return None

            # Extract text from paragraphs within content div
            paragraphs = content_div.find_all('p')
            if paragraphs:
                content = "\n".join([p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True)])
            else:
                # Fallback: get all text from the content div
                content = content_div.get_text(separator="\n", strip=True)

            if not title or not content:
                self.logger.warning(f"Missing title or content for {url}")
                return None

            # Generate story ID from URL
            story_slug = url.split('/stories/')[-1].split('?')[0].rstrip('/')
            story_id = re.sub(r'[^a-zA-Z0-9_-]', '_', story_slug)

            # Try to extract author name
            author = ""
            author_link = soup.select_one('a[href*="/authors/"], a[href*="/storywriter/"]')
            if author_link:
                author = author_link.get_text(strip=True)

            return {
                'id': f"rekhta_{story_id}",
                'title': title,
                'content': content,
                'source': 'rekhta',
                'url': url,
                'author': author,
                'scraped_at': time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
            }

        except Exception as e:
            self.logger.error(f"Error extracting story from {url}: {str(e)}")
            return None
