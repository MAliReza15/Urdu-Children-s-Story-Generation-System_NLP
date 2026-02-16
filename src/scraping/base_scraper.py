from abc import ABC, abstractmethod
import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import time
import random
import logging
from typing import Dict, List, Optional
import json
from pathlib import Path

class BaseScraper(ABC):
    """
    Abstract base class for all website scrapers.
    Includes anti-detection measures: random delays, rotating UAs, referer headers.
    """
    
    def __init__(self, config: Dict, source_name: str):
        self.config = config
        self.source_name = source_name
        self.source_config = config['sources'][source_name]
        
        # Setup
        self.ua = UserAgent()
        self.session = requests.Session()
        self.logger = self._setup_logger()
        
        # Storage
        self.stories = []
        self.failed_urls = []
        self.save_dir = Path(f"data/raw/{source_name}")
        self.save_dir.mkdir(parents=True, exist_ok=True)
        
    def _setup_logger(self) -> logging.Logger:
        logger = logging.getLogger(f"scraper.{self.source_name}")
        logger.setLevel(logging.INFO)
        if not logger.handlers:
            ch = logging.StreamHandler()
            ch.setLevel(logging.INFO)
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            ch.setFormatter(formatter)
            logger.addHandler(ch)
            log_dir = Path(self.config.get('logging', {}).get('log_dir', 'logs/'))
            log_dir.mkdir(exist_ok=True)
            fh = logging.FileHandler(log_dir / "scraping.log", encoding='utf-8')
            fh.setFormatter(formatter)
            logger.addHandler(fh)
        return logger
    
    def _get_headers(self, referer: str = None) -> Dict:
        """Generate realistic browser headers with anti-detection."""
        headers = {
            'User-Agent': self.ua.random,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'ur,en-US;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0',
        }
        if referer:
            headers['Referer'] = referer
        return headers
    
    def _random_delay(self):
        """Random delay between requests to avoid detection."""
        base = self.config.get('scraping', {}).get('delay_between_requests', 3.0)
        delay = base + random.uniform(0.5, 2.0)
        time.sleep(delay)
    
    def fetch_page(self, url: str, retries: int = 3, referer: str = None) -> Optional[BeautifulSoup]:
        """Fetch and parse a webpage with anti-detection."""
        for i in range(retries):
            try:
                self._random_delay()
                
                response = self.session.get(
                    url, 
                    headers=self._get_headers(referer=referer),
                    timeout=self.config.get('scraping', {}).get('timeout', 30),
                    verify=True
                )
                response.raise_for_status()
                response.encoding = 'utf-8'
                return BeautifulSoup(response.content, 'html.parser')
                
            except requests.RequestException as e:
                self.logger.warning(f"Attempt {i+1}/{retries} failed for {url}: {str(e)}")
                if i < retries - 1:
                    time.sleep(5 * (i + 1))  # Exponential backoff
                else:
                    self.logger.error(f"Failed to fetch {url} after {retries} attempts")
                    self.failed_urls.append({'url': url, 'error': str(e)})
                    return None
        return None
    
    def fetch_text(self, url: str, retries: int = 3, referer: str = None) -> Optional[str]:
        """Fetch raw text content of a page."""
        for i in range(retries):
            try:
                self._random_delay()
                response = self.session.get(
                    url,
                    headers=self._get_headers(referer=referer),
                    timeout=self.config.get('scraping', {}).get('timeout', 30),
                    verify=True
                )
                response.raise_for_status()
                response.encoding = 'utf-8'
                return response.text
            except requests.RequestException as e:
                self.logger.warning(f"Attempt {i+1}/{retries} failed for {url}: {str(e)}")
                if i < retries - 1:
                    time.sleep(5 * (i + 1))
                else:
                    self.failed_urls.append({'url': url, 'error': str(e)})
                    return None
        return None

    @abstractmethod
    def get_story_urls(self) -> List[str]:
        """Get list of story URLs to scrape."""
        pass
    
    @abstractmethod
    def extract_story(self, url: str) -> Optional[Dict]:
        """Extract story content from URL."""
        pass
    
    def validate_story(self, story: Dict) -> bool:
        """Validate story meets quality criteria."""
        if not story or not story.get('content') or not story.get('title'):
            return False
            
        word_count = len(story['content'].split())
        validation = self.config.get('validation', {})
        
        min_words = validation.get('min_word_count', 50)
        max_words = validation.get('max_word_count', 10000)
        
        if word_count < min_words:
            self.logger.debug(f"Story too short: {word_count} words (min: {min_words})")
            return False
            
        if word_count > max_words:
            self.logger.debug(f"Story too long: {word_count} words (max: {max_words})")
            return False
            
        return True
    
    def save_story(self, story: Dict) -> None:
        """Save story to JSON file."""
        try:
            filename = f"{story['id']}.json"
            filepath = self.save_dir / filename
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(story, f, ensure_ascii=False, indent=2)
            self.logger.info(f"Saved story: {story['id']}")
        except Exception as e:
            self.logger.error(f"Failed to save story {story.get('id')}: {str(e)}")
    
    def run(self, test_mode: bool = False) -> int:
        """
        Main execution method.
        Args:
            test_mode: If True, scrape only 1 story for testing
        Returns:
            Number of stories successfully scraped
        """
        self.logger.info(f"Starting scraping for {self.source_name}" + (" [TEST MODE]" if test_mode else ""))
        
        story_urls = self.get_story_urls()
        self.logger.info(f"Found {len(story_urls)} potential story URLs")
        
        if not story_urls:
            self.logger.error("No story URLs found!")
            return 0
        
        stories_scraped = 0
        target = 1 if test_mode else self.source_config.get('target_stories', 1000)
        
        for i, url in enumerate(story_urls):
            if stories_scraped >= target:
                self.logger.info(f"Reached target of {target} stories")
                break
                
            self.logger.info(f"Processing {i+1}/{min(len(story_urls), target)}: {url}")
            story = self.extract_story(url)
            
            if story and self.validate_story(story):
                self.save_story(story)
                stories_scraped += 1
            else:
                self.logger.warning(f"Story skipped (invalid/empty): {url}")
                
        self.logger.info(f"Finished {self.source_name}. Scraped {stories_scraped} stories.")
        
        if self.failed_urls:
            fail_path = self.save_dir.parent / f"{self.source_name}_failures.json"
            with open(fail_path, 'w', encoding='utf-8') as f:
                json.dump(self.failed_urls, f, indent=2, ensure_ascii=False)
                
        return stories_scraped
