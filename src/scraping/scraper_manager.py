import yaml
import logging
from typing import Dict, List, Type
from pathlib import Path
import json

from .base_scraper import BaseScraper
from .urdupoint_scraper import UrduPointScraper
from .rekhta_scraper import RekhtaScraper
from .bbc_scraper import BBCScraper

class ScraperManager:
    """Manages multiple scrapers and coordinates scraping operations."""
    
    SCRAPER_CLASSES = {
        'urdupoint': UrduPointScraper,
        'rekhta': RekhtaScraper,
        'bbc_urdu': BBCScraper,
        # 'kitabonagri' and 'urdukahani' removed - sites are offline
    }
    
    def __init__(self, config_path: str):
        self.config_path = Path(config_path)
        with open(self.config_path, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)
            
        self.scrapers: List[BaseScraper] = []
        self._setup_logging()
        
    def _setup_logging(self):
        self.logger = logging.getLogger("ScraperManager")
        self.logger.setLevel(logging.INFO)
        if not self.logger.handlers:
            ch = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            ch.setFormatter(formatter)
            self.logger.addHandler(ch)
    
    def register_scraper(self, source_name: str):
        """Register a scraper for execution."""
        if source_name not in self.SCRAPER_CLASSES:
            self.logger.error(f"Unknown scraper source: {source_name}. Available: {list(self.SCRAPER_CLASSES.keys())}")
            return
            
        if source_name not in self.config.get('sources', {}):
            self.logger.error(f"No configuration found for source: {source_name}")
            return
        
        # Check if enabled
        source_config = self.config['sources'][source_name]
        if not source_config.get('enabled', True):
            self.logger.info(f"Skipping disabled source: {source_name}")
            return
            
        scraper_class = self.SCRAPER_CLASSES[source_name]
        try:
            scraper = scraper_class(self.config)
            self.scrapers.append(scraper)
            self.logger.info(f"Registered scraper: {source_name}")
        except Exception as e:
            self.logger.error(f"Failed to register scraper {source_name}: {str(e)}")
    
    def run_all_scrapers(self, test_mode: bool = False):
        """Execute all registered scrapers."""
        results = {}
        for scraper in self.scrapers:
            try:
                self.logger.info(f"Running scraper: {scraper.source_name}" + (" [TEST]" if test_mode else ""))
                count = scraper.run(test_mode=test_mode)
                results[scraper.source_name] = count
            except Exception as e:
                self.logger.error(f"Scraper {scraper.source_name} failed: {str(e)}")
                results[scraper.source_name] = f"Failed: {str(e)}"
                
        return results
