# Phase 1: Scraping & Preprocessing - Detailed Implementation Plan
## Urdu Story Generation AI Project

---

## 📋 **Phase 1 Overview**

**Goal**: Collect and preprocess 400-500 high-quality Urdu stories ready for tokenizer training.

 
**Output**: Clean, normalized Urdu text corpus with special tokens

---

## 🎯 **Phase 1 Breakdown**

### **Stage 1: Environment Setup** 
### **Stage 2: Scraping Implementation** 
### **Stage 3: Preprocessing Implementation** 
### **Stage 4: Validation & Quality Control** 

---

# STAGE 1: Environment Setup

## 1.1 Project Structure Creation

```
urdu-story-ai/
│
├── data/
│   ├── raw/                          
│   │   ├── urdupoint/
│   │   ├── rekhta/
│   │   ├── kitabonagri/
│   │   ├── bbc_urdu/
│   │   └── urdukahani/
│   │
│   ├── processed/                    
│   │   ├── stories.json              # All cleaned stories
│   │   ├── stories.txt               # Concatenated corpus
│   │   └── stories_with_tokens.txt   # With special tokens
│   │
│   └── metadata/                     
│       ├── scraping_log.json         # Scraping history
│       ├── failed_urls.json          # Failed scrapes
│       └── statistics.json           # Corpus stats
│
├── src/
│   ├── scraping/
│   │   ├── __init__.py
│   │   ├── base_scraper.py           # Abstract base class
│   │   ├── urdupoint_scraper.py
│   │   ├── rekhta_scraper.py
│   │   ├── kitabonagri_scraper.py
│   │   ├── bbc_scraper.py
│   │   ├── urdukahani_scraper.py
│   │   └── scraper_manager.py        # Orchestration
│   │
│   ├── preprocessing/
│   │   ├── __init__.py
│   │   ├── html_cleaner.py           # HTML/tag removal
│   │   ├── text_normalizer.py        # Unicode normalization
│   │   ├── language_filter.py        # Non-Urdu removal
│   │   ├── special_tokens.py         # Token insertion
│   │   └── pipeline.py               # Full preprocessing flow
│   │
│   └── utils/
│       ├── __init__.py
│       ├── file_handler.py
│       ├── logger.py
│       └── validators.py
│
├── config/
│   ├── scraping_config.yaml
│   └── preprocessing_config.yaml
│
├── scripts/
│   ├── run_scraper.py
│   ├── run_preprocessing.py
│   └── generate_statistics.py
│
├── requirements.txt
├── .env
└── README.md
```

## 1.2 Dependencies Installation

**requirements.txt:**
```txt
# Web Scraping
requests==2.31.0
beautifulsoup4==4.12.2
lxml==4.9.3
selenium==4.15.2
webdriver-manager==4.0.1

# Data Processing
pandas==2.1.3
numpy==1.26.2

# Text Processing
regex==2023.10.3
langdetect==1.0.9
python-bidi==0.4.2          # RTL text handling

# Configuration
pyyaml==6.0.1
python-dotenv==1.0.0

# Utilities
tqdm==4.66.1
fake-useragent==1.4.0
colorlog==6.8.0

# Optional (for async scraping)
aiohttp==3.9.1
asyncio==3.4.3
```

**Installation Command:**
```bash
pip install -r requirements.txt
```

## 1.3 Configuration Files

### config/scraping_config.yaml

```yaml
scraping:
  delay_between_requests: 2.5  # seconds
  max_retries: 3
  timeout: 30
  concurrent_requests: 1  # Start conservative
  
  user_agents:
    rotate: true
    pool_size: 10

sources:
  urdupoint:
    base_url: "https://www.urdupoint.com/stories/"
    target_stories: 100
    categories:
      - "moral-stories"
      - "romantic-stories"
      - "funny-stories"
    selectors:
      story_list: "div.story-item a"
      title: "h1.story-title"
      content: "div.story-content p"
    
  rekhta:
    base_url: "https://www.rekhta.org"
    target_stories: 120
    section: "afsaane"
    requires_javascript: true
    selectors:
      story_list: "div.contentList a"
      title: "h1.title"
      content: "div.poemPageContentBody"
    
  kitabonagri:
    base_url: "https://www.kitabonagri.com"
    target_stories: 80
    selectors:
      story_list: "div.book-item a"
      title: "h1.book-title"
      content: "div.book-content"
    
  bbc_urdu:
    base_url: "https://www.bbc.com/urdu"
    target_stories: 60
    topics: "topics/c7zp57yyz0zt"
    selectors:
      story_list: "article a"
      title: "h1.article-headline"
      content: "div.article-body p"
    
  urdukahani:
    base_url: "https://urdukahani.com"
    target_stories: 140
    selectors:
      story_list: "div.kahani-item a"
      title: "h1.kahani-title"
      content: "div.kahani-content p"

validation:
  min_word_count: 100
  max_word_count: 5000
  min_urdu_percentage: 85.0
  max_duplicate_similarity: 0.95
  
logging:
  level: "INFO"
  save_to_file: true
  log_dir: "logs/"
```

### config/preprocessing_config.yaml

```yaml
preprocessing:
  unicode:
    normalization_form: "NFKC"
    urdu_ranges:
      - [0x0600, 0x06FF]  # Arabic/Urdu
      - [0xFB50, 0xFDFF]  # Arabic Presentation Forms-A
      - [0xFE70, 0xFEFF]  # Arabic Presentation Forms-B
      - [0x0750, 0x077F]  # Arabic Supplement
    
  special_tokens:
    story_start: "\uE000"     # U+E000 (Private Use Area)
    story_end: "\uE001"       # U+E001
    paragraph: "\uE002"       # U+E002
    sentence: "\uE003"        # U+E003 (optional for tri-gram)
    
  cleaning:
    remove_urls: true
    remove_emails: true
    remove_numbers_standalone: false  # Keep numbers in context
    remove_english_words: true
    standardize_punctuation: true
    remove_excessive_whitespace: true
    
  punctuation:
    urdu_period: "۔"
    urdu_comma: "،"
    urdu_question: "؟"
    urdu_semicolon: "؛"
    urdu_exclamation: "!"
    
    # Standardization mappings
    standardize:
      ".": "۔"
      ",": "،"
      "?": "؟"
      ";": "؛"
    
  filters:
    min_paragraph_words: 10
    remove_short_sentences: true
    min_sentence_words: 3
    max_consecutive_duplicates: 2  # Remove repeated words
    
  language:
    primary: "ur"  # Urdu
    min_urdu_char_percentage: 85.0
    allowed_scripts:
      - "Arabic"
      - "Common"  # For punctuation, numbers
    
validation:
  check_unicode_validity: true
  check_special_tokens: true
  check_language_purity: true
  generate_report: true
```

---

# STAGE 2: Scraping Implementation

## 2.1 Recommended Websites for Scraping

### Primary Sources (Total Target: 500 stories)

| Website | URL | Target Stories | Content Type | Difficulty |
|---------|-----|----------------|--------------|------------|
| **UrduPoint** | https://www.urdupoint.com/stories/ | 100 | Moral, Romantic, Funny | Easy |
| **Rekhta** | https://www.rekhta.org/ | 120 | Classical & Contemporary | Medium (JS) |
| **Kitab Nagri** | https://www.kitabonagri.com/ | 80 | Books, Stories | Easy |
| **BBC Urdu** | https://www.bbc.com/urdu/topics/c7zp57yyz0zt | 60 | News Features | Easy |
| **UrduKahani** | https://urdukahani.com/ | 140 | Story Platform | Easy |

### Backup Sources (If needed)

- **Jashn-e-Rekhta**: https://jashne-rekhta.org/
- **Humsub**: https://www.humsub.com.pk/category/urdu-kahaniyan/
- **UrduNama**: https://urdunama.org/
- **Local Urdu blogs**

## 2.2 Base Scraper Architecture

### Class Structure

```python
# src/scraping/base_scraper.py

from abc import ABC, abstractmethod
import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import time
import logging
from typing import Dict, List, Optional
import json
from pathlib import Path

class BaseScraper(ABC):
    """
    Abstract base class for all website scrapers.
    Provides common functionality for web scraping.
    """
    
    def __init__(self, config: Dict, source_name: str):
        """
        Initialize scraper with configuration.
        
        Args:
            config: Scraping configuration dictionary
            source_name: Name of the source website
        """
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
        """Setup logging for the scraper."""
        pass
    
    def _get_headers(self) -> Dict:
        """Generate request headers with rotating user agent."""
        pass
    
    def fetch_page(self, url: str, retries: int = 3) -> Optional[BeautifulSoup]:
        """
        Fetch and parse a webpage.
        
        Args:
            url: URL to fetch
            retries: Number of retry attempts
            
        Returns:
            BeautifulSoup object or None if failed
        """
        pass
    
    @abstractmethod
    def get_story_urls(self) -> List[str]:
        """
        Get list of story URLs to scrape.
        Must be implemented by each scraper.
        """
        pass
    
    @abstractmethod
    def extract_story(self, url: str) -> Optional[Dict]:
        """
        Extract story content from URL.
        Must be implemented by each scraper.
        
        Returns:
            Dictionary with story data or None if failed
        """
        pass
    
    def validate_story(self, story: Dict) -> bool:
        """
        Validate story meets quality criteria.
        
        Args:
            story: Story dictionary
            
        Returns:
            True if valid, False otherwise
        """
        pass
    
    def save_story(self, story: Dict) -> None:
        """Save story to JSON file."""
        pass
    
    def save_batch(self, batch_num: int) -> None:
        """Save batch of stories."""
        pass
    
    def run(self) -> int:
        """
        Main execution method.
        
        Returns:
            Number of stories successfully scraped
        """
        pass
```

### Key Methods Implementation Details

**fetch_page():**
- Add delays between requests (2.5 seconds)
- Rotate user agents
- Handle timeouts and exceptions
- Retry on failure (max 3 attempts)
- Log all requests

**validate_story():**
- Check word count (100-5000 words)
- Verify Urdu content percentage (>85%)
- Check for required fields (title, content)
- Detect language using langdetect

**save_story():**
- Save incrementally (every 10 stories)
- Store in JSON format
- Include metadata (timestamp, source, URL)
- Log save operations

## 2.3 Site-Specific Scraper Implementations

### 2.3.1 UrduPoint Scraper

**Website Analysis:**
- Structure: Category → Story List → Individual Stories
- Categories: moral-stories, romantic-stories, funny-stories
- Pagination: Yes
- JavaScript: No

**Implementation Strategy:**

```python
# src/scraping/urdupoint_scraper.py

class UrduPointScraper(BaseScraper):
    """Scraper for UrduPoint.com stories"""
    
    def __init__(self, config: Dict):
        super().__init__(config, 'urdupoint')
        self.base_url = self.source_config['base_url']
        self.categories = self.source_config['categories']
        
    def get_category_urls(self) -> List[str]:
        """Get URLs for all story categories."""
        # Return list of category URLs
        pass
    
    def get_story_urls_from_category(self, category_url: str) -> List[str]:
        """
        Extract story URLs from a category page.
        Handle pagination if present.
        """
        pass
    
    def get_story_urls(self) -> List[str]:
        """Combine URLs from all categories."""
        pass
    
    def extract_story(self, url: str) -> Optional[Dict]:
        """
        Extract story from UrduPoint page.
        
        Expected structure:
        - Title: h1.story-title
        - Content: div.story-content p
        - Metadata: author, date, category
        """
        pass
```

**CSS Selectors (to be verified during scraping):**
```python
SELECTORS = {
    'story_list': 'div.story-item a',
    'title': 'h1.story-title',
    'content': 'div.story-content p',
    'author': 'span.author-name',
    'date': 'span.publish-date',
    'category': 'span.category'
}
```

**Expected Output:**
- 100 stories total
- Average: 300-500 words per story
- Categories: Balanced across 3 categories

### 2.3.2 Rekhta Scraper 

**Website Analysis:**
- Structure: Section (Afsaane) → Story List → Story Pages
- JavaScript: Yes (may require Selenium)
- High-quality literary content
- Metadata rich (author, year, etc.)

**Implementation Strategy:**

```python
# src/scraping/rekhta_scraper.py

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

class RekhtaScraper(BaseScraper):
    """Scraper for Rekhta.org (requires Selenium for JS rendering)"""
    
    def __init__(self, config: Dict):
        super().__init__(config, 'rekhta')
        self.driver = None
        self._setup_selenium()
        
    def _setup_selenium(self):
        """Initialize Selenium WebDriver."""
        # Setup headless Chrome
        pass
    
    def get_story_urls(self) -> List[str]:
        """Navigate Afsaane section and collect story URLs."""
        pass
    
    def extract_story(self, url: str) -> Optional[Dict]:
        """
        Extract story using Selenium.
        Handle special Unicode rendering.
        """
        pass
    
    def __del__(self):
        """Cleanup: Close Selenium driver."""
        if self.driver:
            self.driver.quit()
```

**Expected Output:**
- 120 stories
- Average: 400-800 words per story
- Classical and contemporary literature

### 2.3.3 Kitab Nagri Scraper 

**Implementation Strategy:**

```python
# src/scraping/kitabonagri_scraper.py

class KitabNagriScraper(BaseScraper):
    """Scraper for KitabONagri.com"""
    
    def get_story_urls(self) -> List[str]:
        """
        Navigate book sections.
        May need to handle PDF extractions if stories are in PDF format.
        """
        pass
    
    def extract_story(self, url: str) -> Optional[Dict]:
        """Extract story from HTML or PDF."""
        pass
    
    def extract_from_pdf(self, pdf_url: str) -> Optional[str]:
        """If needed: Extract text from PDF using PyPDF2 or pdfplumber."""
        pass
```

**Expected Output:**
- 80 stories
- Average: 500-1000 words per story

### 2.3.4 BBC Urdu Scraper 

**Implementation Strategy:**

```python
# src/scraping/bbc_scraper.py

class BBCScraper(BaseScraper):
    """Scraper for BBC Urdu stories"""
    
    def get_story_urls(self) -> List[str]:
        """
        Get URLs from topics section.
        Filter for feature stories (not news).
        """
        pass
    
    def extract_story(self, url: str) -> Optional[Dict]:
        """
        Extract BBC article.
        
        Selectors:
        - Title: h1.article-headline
        - Content: div.article-body p
        """
        pass
    
    def is_feature_story(self, soup: BeautifulSoup) -> bool:
        """Distinguish feature stories from news articles."""
        pass
```

**Expected Output:**
- 60 stories
- Average: 200-400 words per story

### 2.3.5 UrduKahani Scraper 

**Implementation Strategy:**

```python
# src/scraping/urdukahani_scraper.py

class UrduKahaniScraper(BaseScraper):
    """Scraper for UrduKahani.com"""
    
    def get_story_urls(self) -> List[str]:
        """
        Navigate all categories.
        Handle pagination.
        """
        pass
    
    def extract_story(self, url: str) -> Optional[Dict]:
        """Extract story from UrduKahani page."""
        pass
```

**Expected Output:**
- 140 stories
- Average: 300-600 words per story

## 2.4 Scraper Manager 

**Purpose**: Orchestrate all scrapers, handle failures, merge results

```python
# src/scraping/scraper_manager.py

class ScraperManager:
    """Manages multiple scrapers and coordinates scraping operations"""
    
    def __init__(self, config_path: str):
        """Initialize with configuration file."""
        pass
    
    def register_scraper(self, scraper_class, source_name: str):
        """Register a scraper for execution."""
        pass
    
    def run_all_scrapers(self, parallel: bool = False):
        """
        Execute all registered scrapers.
        
        Args:
            parallel: Run scrapers concurrently (not recommended initially)
        """
        pass
    
    def merge_results(self) -> List[Dict]:
        """Combine results from all scrapers."""
        pass
    
    def generate_report(self) -> Dict:
        """Generate scraping statistics and report."""
        pass
    
    def handle_failures(self):
        """Retry failed URLs or log for manual review."""
        pass
```

## 2.5 Scraping Execution Plan 

### Testing Phase

**Step 1: Test Individual Scrapers**
```bash
# Test each scraper with 5 stories
python scripts/test_scraper.py --source urdupoint --limit 5
python scripts/test_scraper.py --source rekhta --limit 5
# ... etc
```

**Step 2: Verify Data Quality**
- Check story structure
- Validate Urdu content
- Verify metadata completeness

### Production Scraping

**Execution Order:**
1. UrduPoint: 100 stories (~2-3 hours)
2. Rekhta: 120 stories (~3-4 hours with Selenium)
3. Kitab Nagri: 80 stories (~2 hours)
4. BBC Urdu: 60 stories (~1-2 hours)
5. UrduKahani: 140 stories (~3-4 hours)

**Total Time: ~12-15 hours** (with delays)

### Execution Commands

```bash
# Run full scraping pipeline
python scripts/run_scraper.py --all

# Or run individual scrapers
python scripts/run_scraper.py --source urdupoint
python scripts/run_scraper.py --source rekhta
# ... etc

# Generate scraping report
python scripts/generate_statistics.py --phase scraping
```

### Output Format

Each story saved as:
```json
{
  "id": "urdupoint_001",
  "title": "اخلاقی کہانی - ایمانداری کی جیت",
  "content": "یہ ایک دن کی بات ہے جب ایک غریب لڑکا...",
  "source": "urdupoint",
  "category": "moral",
  "url": "https://www.urdupoint.com/stories/...",
  "scraped_at": "2024-02-16T10:30:00Z",
  "word_count": 456,
  "paragraph_count": 8,
  "character_count": 2345,
  "language_confidence": 0.99,
  "metadata": {
    "author": "احمد علی",
    "publish_date": "2023-12-15"
  }
}
```

---

# STAGE 3: Preprocessing Implementation

## 3.1 HTML Cleaner 

### Purpose
Remove all HTML artifacts and clean raw text.

### Implementation

```python
# src/preprocessing/html_cleaner.py

import re
from bs4 import BeautifulSoup
import html

class HTMLCleaner:
    """Removes HTML tags and cleans text"""
    
    @staticmethod
    def clean(text: str) -> str:
        """
        Main cleaning pipeline.
        
        Args:
            text: Raw text with potential HTML
            
        Returns:
            Cleaned text
        """
        # 1. Remove scripts and styles
        text = HTMLCleaner._remove_scripts_styles(text)
        
        # 2. Parse HTML and extract text
        text = HTMLCleaner._extract_text_from_html(text)
        
        # 3. Decode HTML entities
        text = html.unescape(text)
        
        # 4. Remove HTML comments
        text = re.sub(r'<!--.*?-->', '', text, flags=re.DOTALL)
        
        # 5. Clean whitespace
        text = HTMLCleaner._clean_whitespace(text)
        
        return text
    
    @staticmethod
    def _remove_scripts_styles(text: str) -> str:
        """Remove script and style tags."""
        pass
    
    @staticmethod
    def _extract_text_from_html(text: str) -> str:
        """Extract text using BeautifulSoup."""
        pass
    
    @staticmethod
    def _clean_whitespace(text: str) -> str:
        """Normalize whitespace."""
        pass
```

### Cleaning Examples

```python
# Example 1: HTML tags
Input:  "<p>یہ <strong>کہانی</strong> ہے۔</p>"
Output: "یہ کہانی ہے۔"

# Example 2: HTML entities
Input:  "یہ&nbsp;کہانی&nbsp;ہے۔"
Output: "یہ کہانی ہے۔"

# Example 3: Scripts
Input:  "<script>alert('test')</script>یہ کہانی ہے۔"
Output: "یہ کہانی ہے۔"
```

## 3.2 Text Normalizer 

### Purpose
Standardize Unicode and text formatting for Urdu.

### Implementation

```python
# src/preprocessing/text_normalizer.py

import unicodedata
import re
from typing import Dict

class TextNormalizer:
    """Normalizes Urdu text and Unicode"""
    
    # Urdu Unicode ranges
    URDU_RANGES = [
        (0x0600, 0x06FF),  # Arabic/Urdu
        (0xFB50, 0xFDFF),  # Arabic Presentation Forms-A
        (0xFE70, 0xFEFF),  # Arabic Presentation Forms-B
        (0x0750, 0x077F),  # Arabic Supplement
    ]
    
    # Character standardization mappings
    CHAR_MAPPINGS = {
        'ك': 'ک',  # Arabic kaf → Urdu kaf
        'ي': 'ی',  # Arabic yeh → Urdu yeh
        'ى': 'ی',  # Alef maksura → Urdu yeh
        'ہ': 'ہ',  # Standardize heh
        # Add more mappings as needed
    }
    
    def __init__(self, config: Dict):
        self.config = config
        self.normalization_form = config['unicode']['normalization_form']
        
    def normalize(self, text: str) -> str:
        """
        Main normalization pipeline.
        
        Args:
            text: Text to normalize
            
        Returns:
            Normalized text
        """
        # 1. Unicode normalization (NFKC)
        text = unicodedata.normalize(self.normalization_form, text)
        
        # 2. Standardize Urdu characters
        text = self._standardize_characters(text)
        
        # 3. Remove/normalize zero-width characters
        text = self._handle_zero_width_chars(text)
        
        # 4. Standardize punctuation
        text = self._standardize_punctuation(text)
        
        # 5. Normalize whitespace
        text = self._normalize_whitespace(text)
        
        # 6. Fix RTL issues
        text = self._fix_rtl_issues(text)
        
        return text
    
    def _standardize_characters(self, text: str) -> str:
        """Replace character variations with standard forms."""
        for old_char, new_char in self.CHAR_MAPPINGS.items():
            text = text.replace(old_char, new_char)
        return text
    
    def _handle_zero_width_chars(self, text: str) -> str:
        """
        Handle zero-width joiners and non-joiners.
        Remove where inappropriate, keep where necessary for Urdu.
        """
        pass
    
    def _standardize_punctuation(self, text: str) -> str:
        """
        Standardize punctuation marks to Urdu variants.
        
        . → ۔ (Urdu period)
        , → ، (Urdu comma)
        ? → ؟ (Urdu question mark)
        """
        punct_map = self.config['punctuation']['standardize']
        for eng_punct, urdu_punct in punct_map.items():
            text = text.replace(eng_punct, urdu_punct)
        return text
    
    def _normalize_whitespace(self, text: str) -> str:
        """
        Normalize all whitespace.
        - Replace multiple spaces with single space
        - Remove spaces around punctuation
        - Normalize newlines
        """
        pass
    
    def _fix_rtl_issues(self, text: str) -> str:
        """Fix right-to-left text rendering issues."""
        pass
```

### Normalization Examples

```python
# Example 1: Character standardization
Input:  "یہ كہانی ہے۔"  (Arabic kaf)
Output: "یہ کہانی ہے۔"  (Urdu kaf)

# Example 2: Punctuation
Input:  "یہ کہانی ہے."  (English period)
Output: "یہ کہانی ہے۔"  (Urdu period)

# Example 3: Whitespace
Input:  "یہ    کہانی   ہے۔"  (irregular spacing)
Output: "یہ کہانی ہے۔"

# Example 4: Mixed punctuation
Input:  "کیا یہ اچھی ہے?"
Output: "کیا یہ اچھی ہے؟"
```

## 3.3 Language Filter 

### Purpose
Remove non-Urdu content and ensure language purity.

### Implementation

```python
# src/preprocessing/language_filter.py

import re
from langdetect import detect, detect_langs
from typing import Tuple

class LanguageFilter:
    """Filters non-Urdu content from text"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.min_urdu_percentage = config['language']['min_urdu_char_percentage']
        
    def filter(self, text: str) -> str:
        """
        Main filtering pipeline.
        
        Args:
            text: Text to filter
            
        Returns:
            Filtered text with non-Urdu content removed
        """
        # 1. Check overall Urdu percentage
        urdu_pct = self.calculate_urdu_percentage(text)
        if urdu_pct < self.min_urdu_percentage:
            return ""  # Reject entire text
        
        # 2. Remove English sentences
        text = self._remove_english_sentences(text)
        
        # 3. Remove standalone English words
        text = self._remove_english_words(text)
        
        # 4. Remove Arabic-only paragraphs (keep Urdu-Arabic mix)
        text = self._filter_arabic_only(text)
        
        # 5. Final validation
        final_pct = self.calculate_urdu_percentage(text)
        if final_pct < self.min_urdu_percentage:
            return ""
        
        return text
    
    def calculate_urdu_percentage(self, text: str) -> float:
        """
        Calculate percentage of Urdu characters.
        
        Returns:
            Percentage (0-100) of Urdu/Arabic script characters
        """
        if not text:
            return 0.0
        
        total_chars = len(text)
        urdu_chars = sum(1 for c in text if self._is_urdu_char(c))
        
        return (urdu_chars / total_chars) * 100
    
    def _is_urdu_char(self, char: str) -> bool:
        """Check if character is in Urdu Unicode ranges."""
        code = ord(char)
        urdu_ranges = self.config['unicode']['urdu_ranges']
        
        for start, end in urdu_ranges:
            if start <= code <= end:
                return True
        return False
    
    def _remove_english_sentences(self, text: str) -> str:
        """
        Remove sentences that are primarily English.
        Split by Urdu sentence delimiter (۔) and filter.
        """
        pass
    
    def _remove_english_words(self, text: str) -> str:
        """
        Remove standalone English words using regex.
        Keep numbers in Urdu context.
        """
        # Pattern: English words (but preserve Urdu)
        pattern = r'\b[a-zA-Z]+\b'
        text = re.sub(pattern, '', text)
        return text
    
    def _filter_arabic_only(self, text: str) -> str:
        """
        Remove paragraphs that are purely Arabic (not Urdu).
        This is tricky as Urdu uses Arabic script.
        Use heuristics like presence of Urdu-specific characters.
        """
        pass
    
    def detect_language(self, text: str) -> str:
        """
        Detect language using langdetect.
        
        Returns:
            Language code ('ur' for Urdu)
        """
        try:
            return detect(text)
        except:
            return "unknown"
    
    def is_valid_urdu_text(self, text: str) -> Tuple[bool, float]:
        """
        Validate if text is valid Urdu.
        
        Returns:
            (is_valid, urdu_percentage)
        """
        urdu_pct = self.calculate_urdu_percentage(text)
        is_valid = urdu_pct >= self.min_urdu_percentage
        return is_valid, urdu_pct
```

### Filtering Examples

```python
# Example 1: English sentences
Input:  "یہ کہانی ہے۔ This is a story. یہ اچھی ہے۔"
Output: "یہ کہانی ہے۔ یہ اچھی ہے۔"

# Example 2: English words
Input:  "یہ story بہت good ہے۔"
Output: "یہ بہت ہے۔"

# Example 3: Calculate Urdu percentage
Input:  "یہ کہانی ہے ABC"
Output: 83.3% (10 Urdu chars out of 12 total)
```

## 3.4 Special Tokens Insertion

### Purpose
Add structural tokens for model training using Private Use Area Unicode.

### Implementation

```python
# src/preprocessing/special_tokens.py

import re

class SpecialTokens:
    """Manages special tokens for story structure"""
    
    # Unicode Private Use Area (U+E000 to U+F8FF)
    STORY_START = '\uE000'  # 
    STORY_END = '\uE001'    # 
    PARAGRAPH = '\uE002'    # 
    SENTENCE = '\uE003'     # 
    
    def __init__(self, config: Dict):
        self.config = config
        # Override with config if provided
        tokens = config.get('special_tokens', {})
        self.STORY_START = tokens.get('story_start', self.STORY_START)
        self.STORY_END = tokens.get('story_end', self.STORY_END)
        self.PARAGRAPH = tokens.get('paragraph', self.PARAGRAPH)
        self.SENTENCE = tokens.get('sentence', self.SENTENCE)
    
    def insert_story_markers(self, text: str) -> str:
        """
        Wrap entire story with start/end markers.
        
        Args:
            text: Story text
            
        Returns:
            Text with STORY_START at beginning, STORY_END at end
        """
        return f"{self.STORY_START}{text}{self.STORY_END}"
    
    def insert_paragraph_markers(self, text: str) -> str:
        """
        Insert PARAGRAPH token between paragraphs.
        
        Strategy:
        - Split on double newlines (paragraph breaks)
        - Insert PARAGRAPH token between them
        """
        # Split by paragraph breaks (2+ newlines)
        paragraphs = re.split(r'\n\s*\n', text)
        
        # Join with PARAGRAPH token
        return self.PARAGRAPH.join(p.strip() for p in paragraphs if p.strip())
    
    def insert_sentence_markers(self, text: str) -> str:
        """
        Insert SENTENCE token between sentences (optional for tri-gram).
        
        Strategy:
        - Split on Urdu sentence delimiters (۔ ؟ !)
        - Insert SENTENCE token
        """
        # Split by Urdu sentence endings
        sentences = re.split(r'([۔؟!])', text)
        
        # Reconstruct with markers
        result = []
        for i in range(0, len(sentences)-1, 2):
            if sentences[i].strip():
                result.append(sentences[i].strip() + sentences[i+1])
        
        return self.SENTENCE.join(result)
    
    def insert_all_tokens(self, text: str, include_sentence: bool = False) -> str:
        """
        Insert all structural tokens.
        
        Args:
            text: Original text
            include_sentence: Whether to include sentence markers
            
        Returns:
            Text with all tokens inserted
        """
        # Order matters!
        # 1. Paragraphs first
        text = self.insert_paragraph_markers(text)
        
        # 2. Sentences (optional)
        if include_sentence:
            text = self.insert_sentence_markers(text)
        
        # 3. Story markers (wraps everything)
        text = self.insert_story_markers(text)
        
        return text
    
    def remove_all_tokens(self, text: str) -> str:
        """Remove all special tokens (for display purposes)."""
        tokens = [self.STORY_START, self.STORY_END, self.PARAGRAPH, self.SENTENCE]
        for token in tokens:
            text = text.replace(token, '')
        return text
    
    def get_token_statistics(self, text: str) -> Dict:
        """
        Get statistics about token usage.
        
        Returns:
            Dictionary with counts of each token type
        """
        return {
            'story_start': text.count(self.STORY_START),
            'story_end': text.count(self.STORY_END),
            'paragraph': text.count(self.PARAGRAPH),
            'sentence': text.count(self.SENTENCE),
        }
```

### Token Insertion Examples

```python
# Example 1: Paragraph markers
Input:  "یہ پہلا پیراگراف ہے۔\n\nیہ دوسرا پیراگراف ہے۔"
Output: "یہ پہلا پیراگراف ہے۔یہ دوسرا پیراگراف ہے۔"

# Example 2: Story markers
Input:  "یہ کہانی ہے۔"
Output: "یہ کہانی ہے۔"

# Example 3: All tokens (visual representation)
Input:  "یہ پہلا پیراگراف ہے۔\n\nیہ دوسرا ہے۔"
Output: "<STORY>یہ پہلا پیراگراف ہے۔<PARA>یہ دوسرا ہے۔</STORY>"
```

## 3.5 Preprocessing Pipeline 

### Purpose
Unified pipeline combining all preprocessing steps.

### Implementation

```python
# src/preprocessing/pipeline.py

from typing import Dict, List, Optional
import json
from pathlib import Path
import logging

from .html_cleaner import HTMLCleaner
from .text_normalizer import TextNormalizer
from .language_filter import LanguageFilter
from .special_tokens import SpecialTokens
from ..utils.validators import DataValidator

class PreprocessingPipeline:
    """
    Complete preprocessing pipeline for Urdu stories.
    
    Pipeline stages:
    1. HTML Cleaning
    2. Text Normalization
    3. Language Filtering
    4. Validation
    5. Special Token Insertion
    6. Final Validation
    """
    
    def __init__(self, config_path: str):
        """Initialize pipeline with configuration."""
        with open(config_path) as f:
            self.config = yaml.safe_load(f)['preprocessing']
        
        # Initialize components
        self.html_cleaner = HTMLCleaner()
        self.normalizer = TextNormalizer(self.config)
        self.lang_filter = LanguageFilter(self.config)
        self.special_tokens = SpecialTokens(self.config)
        self.validator = DataValidator(self.config)
        
        # Statistics
        self.stats = {
            'total_processed': 0,
            'successful': 0,
            'failed': 0,
            'rejected_low_quality': 0,
            'rejected_language': 0,
            'failures': []
        }
        
        self.logger = logging.getLogger(__name__)
    
    def process_story(self, raw_story: Dict) -> Optional[Dict]:
        """
        Process a single story through the pipeline.
        
        Args:
            raw_story: Raw story dictionary with 'content' field
            
        Returns:
            Processed story dictionary or None if rejected
        """
        try:
            story_id = raw_story.get('id', 'unknown')
            self.logger.info(f"Processing story: {story_id}")
            
            # Extract content
            content = raw_story.get('content', '')
            if not content:
                self.stats['failed'] += 1
                return None
            
            # Stage 1: HTML Cleaning
            content = self.html_cleaner.clean(content)
            
            # Stage 2: Text Normalization
            content = self.normalizer.normalize(content)
            
            # Stage 3: Language Filtering
            content = self.lang_filter.filter(content)
            if not content:
                self.logger.warning(f"Story {story_id} rejected: language filter")
                self.stats['rejected_language'] += 1
                return None
            
            # Stage 4: Quality Validation
            is_valid, reason = self.validator.validate_content(content)
            if not is_valid:
                self.logger.warning(f"Story {story_id} rejected: {reason}")
                self.stats['rejected_low_quality'] += 1
                return None
            
            # Stage 5: Special Token Insertion
            content_with_tokens = self.special_tokens.insert_all_tokens(
                content, 
                include_sentence=False  # Not needed for tri-gram
            )
            
            # Stage 6: Final Validation
            token_stats = self.special_tokens.get_token_statistics(content_with_tokens)
            if not self.validator.validate_tokens(token_stats):
                self.logger.error(f"Story {story_id} failed token validation")
                self.stats['failed'] += 1
                return None
            
            # Create processed story
            processed_story = {
                **raw_story,
                'content_clean': content,
                'content_with_tokens': content_with_tokens,
                'preprocessing_stats': {
                    'word_count': len(content.split()),
                    'char_count': len(content),
                    'urdu_percentage': self.lang_filter.calculate_urdu_percentage(content),
                    'token_stats': token_stats
                },
                'processed_at': datetime.utcnow().isoformat()
            }
            
            self.stats['successful'] += 1
            return processed_story
            
        except Exception as e:
            self.logger.error(f"Error processing story {story_id}: {str(e)}")
            self.stats['failed'] += 1
            self.stats['failures'].append({
                'id': story_id,
                'error': str(e)
            })
            return None
    
    def process_corpus(self, input_path: str, output_path: str, 
                       batch_size: int = 50) -> Dict:
        """
        Process entire corpus of stories.
        
        Args:
            input_path: Path to raw stories JSON
            output_path: Path to save processed stories
            batch_size: Save after processing this many stories
            
        Returns:
            Processing statistics
        """
        self.logger.info(f"Starting corpus processing: {input_path}")
        
        # Load raw stories
        with open(input_path) as f:
            raw_stories = json.load(f)
        
        self.stats['total_processed'] = len(raw_stories)
        processed_stories = []
        
        # Process each story
        for i, raw_story in enumerate(raw_stories, 1):
            processed = self.process_story(raw_story)
            
            if processed:
                processed_stories.append(processed)
            
            # Save batch
            if i % batch_size == 0:
                self._save_batch(processed_stories, output_path, i)
                self.logger.info(f"Processed {i}/{len(raw_stories)} stories")
        
        # Final save
        self._save_final(processed_stories, output_path)
        
        # Generate report
        self._generate_report(output_path)
        
        return self.stats
    
    def _save_batch(self, stories: List[Dict], output_path: str, batch_num: int):
        """Save intermediate batch."""
        pass
    
    def _save_final(self, stories: List[Dict], output_path: str):
        """Save final processed corpus."""
        # Save as JSON
        json_path = Path(output_path) / 'stories.json'
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(stories, f, ensure_ascii=False, indent=2)
        
        # Save as plain text (without tokens)
        txt_path = Path(output_path) / 'stories.txt'
        with open(txt_path, 'w', encoding='utf-8') as f:
            for story in stories:
                f.write(story['content_clean'] + '\n\n')
        
        # Save as text with tokens
        tokens_path = Path(output_path) / 'stories_with_tokens.txt'
        with open(tokens_path, 'w', encoding='utf-8') as f:
            for story in stories:
                f.write(story['content_with_tokens'] + '\n')
    
    def _generate_report(self, output_path: str):
        """Generate preprocessing report."""
        pass
```

## 3.6 Validation & Quality Control 

### Implementation

```python
# src/utils/validators.py

class DataValidator:
    """Validates data quality at various pipeline stages"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.min_words = config['validation']['min_word_count']
        self.max_words = config['validation']['max_word_count']
        self.min_urdu_pct = config['validation']['min_urdu_percentage']
    
    def validate_content(self, text: str) -> Tuple[bool, str]:
        """
        Validate text content quality.
        
        Returns:
            (is_valid, rejection_reason)
        """
        # Check word count
        words = text.split()
        word_count = len(words)
        
        if word_count < self.min_words:
            return False, f"Too short ({word_count} words)"
        
        if word_count > self.max_words:
            return False, f"Too long ({word_count} words)"
        
        # Check if text is mostly empty/whitespace
        if len(text.strip()) < 50:
            return False, "Mostly empty content"
        
        return True, "Valid"
    
    def validate_tokens(self, token_stats: Dict) -> bool:
        """
        Validate special tokens are correctly inserted.
        
        Expected:
        - story_start: 1
        - story_end: 1
        - paragraph: >= 0
        """
        if token_stats['story_start'] != 1:
            return False
        if token_stats['story_end'] != 1:
            return False
        # Paragraphs can be 0 for short stories
        return True
    
    def detect_duplicate(self, text: str, existing_texts: List[str], 
                        threshold: float = 0.95) -> bool:
        """
        Detect if text is duplicate/near-duplicate.
        
        Uses similarity threshold.
        """
        pass
    
    def validate_unicode(self, text: str) -> bool:
        """Validate all characters are valid Unicode."""
        try:
            text.encode('utf-8')
            return True
        except UnicodeEncodeError:
            return False
```

---

# STAGE 4: Final Validation & Statistics

## 4.1 Generate Corpus Statistics 

### Statistics Script

```python
# scripts/generate_statistics.py

import json
from pathlib import Path
from collections import Counter
import matplotlib.pyplot as plt

class CorpusAnalyzer:
    """Analyzes and generates statistics for the corpus"""
    
    def __init__(self, corpus_path: str):
        self.corpus_path = Path(corpus_path)
        self.stories = self._load_stories()
        
    def _load_stories(self) -> List[Dict]:
        """Load processed stories."""
        with open(self.corpus_path / 'stories.json') as f:
            return json.load(f)
    
    def generate_statistics(self) -> Dict:
        """Generate comprehensive statistics."""
        
        stats = {
            'overview': self._overview_stats(),
            'sources': self._source_distribution(),
            'quality_metrics': self._quality_metrics(),
            'vocabulary': self._vocabulary_stats(),
            'length_distribution': self._length_distribution(),
        }
        
        return stats
    
    def _overview_stats(self) -> Dict:
        """Basic overview statistics."""
        total_words = sum(s['preprocessing_stats']['word_count'] for s in self.stories)
        total_chars = sum(s['preprocessing_stats']['char_count'] for s in self.stories)
        
        return {
            'total_stories': len(self.stories),
            'total_words': total_words,
            'total_characters': total_chars,
            'average_story_length': total_words / len(self.stories),
            'average_char_length': total_chars / len(self.stories),
        }
    
    def _source_distribution(self) -> Dict:
        """Distribution across sources."""
        sources = Counter(s['source'] for s in self.stories)
        return dict(sources)
    
    def _quality_metrics(self) -> Dict:
        """Quality-related metrics."""
        urdu_percentages = [
            s['preprocessing_stats']['urdu_percentage'] 
            for s in self.stories
        ]
        
        return {
            'average_urdu_percentage': sum(urdu_percentages) / len(urdu_percentages),
            'min_urdu_percentage': min(urdu_percentages),
            'max_urdu_percentage': max(urdu_percentages),
        }
    
    def _vocabulary_stats(self) -> Dict:
        """Vocabulary statistics."""
        # Combine all text
        all_text = ' '.join(s['content_clean'] for s in self.stories)
        words = all_text.split()
        
        unique_words = set(words)
        unique_chars = set(all_text)
        
        return {
            'total_words': len(words),
            'unique_words': len(unique_words),
            'unique_characters': len(unique_chars),
            'vocabulary_richness': len(unique_words) / len(words),
        }
    
    def _length_distribution(self) -> Dict:
        """Story length distribution."""
        lengths = [s['preprocessing_stats']['word_count'] for s in self.stories]
        
        return {
            'min': min(lengths),
            'max': max(lengths),
            'median': sorted(lengths)[len(lengths)//2],
            'quartiles': {
                'q1': sorted(lengths)[len(lengths)//4],
                'q3': sorted(lengths)[3*len(lengths)//4],
            }
        }
    
    def save_report(self, output_path: str):
        """Save statistics report."""
        stats = self.generate_statistics()
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(stats, f, ensure_ascii=False, indent=2)
        
        print(json.dumps(stats, ensure_ascii=False, indent=2))
```

### Expected Statistics Output

```json
{
  "overview": {
    "total_stories": 487,
    "total_words": 234567,
    "total_characters": 1456789,
    "average_story_length": 481.6,
    "average_char_length": 2991.4
  },
  "sources": {
    "urdupoint": 98,
    "rekhta": 115,
    "kitabonagri": 78,
    "bbc_urdu": 56,
    "urdukahani": 140
  },
  "quality_metrics": {
    "average_urdu_percentage": 94.5,
    "min_urdu_percentage": 86.2,
    "max_urdu_percentage": 99.8
  },
  "vocabulary": {
    "total_words": 234567,
    "unique_words": 12345,
    "unique_characters": 87,
    "vocabulary_richness": 0.0526
  },
  "length_distribution": {
    "min": 102,
    "max": 2456,
    "median": 423,
    "quartiles": {
      "q1": 298,
      "q3": 612
    }
  }
}
```

## 4.2 Create Final Outputs 

### Output Files Structure

```
data/processed/
├── stories.json                  # Full stories with metadata
├── stories.txt                   # Plain text corpus (no tokens)
├── stories_with_tokens.txt       # Text with special tokens (for training)
├── vocabulary.txt                # Unique words list
├── statistics.json               # Corpus statistics
└── quality_report.txt            # Human-readable report
```

### File Generation Script

```python
# scripts/create_final_outputs.py

def create_vocabulary_file(stories: List[Dict], output_path: str):
    """Extract and save unique vocabulary."""
    all_words = set()
    for story in stories:
        words = story['content_clean'].split()
        all_words.update(words)
    
    # Sort by frequency
    word_freq = Counter()
    for story in stories:
        words = story['content_clean'].split()
        word_freq.update(words)
    
    # Save sorted by frequency
    with open(output_path, 'w', encoding='utf-8') as f:
        for word, freq in word_freq.most_common():
            f.write(f"{word}\t{freq}\n")

def create_quality_report(stats: Dict, output_path: str):
    """Generate human-readable quality report."""
    report = f"""
# Urdu Story Corpus - Quality Report

## Overview
- Total Stories: {stats['overview']['total_stories']}
- Total Words: {stats['overview']['total_words']:,}
- Average Story Length: {stats['overview']['average_story_length']:.1f} words

## Source Distribution
"""
    for source, count in stats['sources'].items():
        report += f"- {source}: {count} stories\n"
    
    report += f"""
## Quality Metrics
- Average Urdu Purity: {stats['quality_metrics']['average_urdu_percentage']:.1f}%
- Unique Words: {stats['vocabulary']['unique_words']:,}
- Vocabulary Richness: {stats['vocabulary']['vocabulary_richness']:.4f}

## Length Distribution
- Minimum: {stats['length_distribution']['min']} words
- Maximum: {stats['length_distribution']['max']} words
- Median: {stats['length_distribution']['median']} words
"""
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(report)
```

## 4.3 Manual Quality Check 

### Quality Assurance Checklist

```
Phase 1 Quality Assurance Checklist
====================================

Dataset Completeness:
[ ] 400-500 stories collected
[ ] All sources represented
[ ] No missing files

Data Quality:
[ ] Random sample of 20 stories reviewed
[ ] All stories are readable Urdu
[ ] No HTML artifacts present
[ ] Unicode rendering correct
[ ] Special tokens correctly placed

Technical Validation:
[ ] stories.json is valid JSON
[ ] stories_with_tokens.txt contains tokens
[ ] No encoding errors
[ ] File sizes reasonable

Statistics:
[ ] Average Urdu percentage > 90%
[ ] Vocabulary size 10K-15K words
[ ] No stories under 100 words
[ ] No duplicate stories

Documentation:
[ ] All logs present
[ ] Failed URLs documented
[ ] Statistics report generated
[ ] README updated
```

### Sample Review Script

```python
# scripts/manual_review.py

import random
import json

def sample_stories_for_review(stories_path: str, sample_size: int = 20):
    """Select random stories for manual review."""
    
    with open(stories_path) as f:
        stories = json.load(f)
    
    # Random sample
    sample = random.sample(stories, sample_size)
    
    # Display for review
    for i, story in enumerate(sample, 1):
        print(f"\n{'='*80}")
        print(f"Story {i}/{sample_size}")
        print(f"ID: {story['id']}")
        print(f"Source: {story['source']}")
        print(f"Title: {story['title']}")
        print(f"Words: {story['preprocessing_stats']['word_count']}")
        print(f"Urdu %: {story['preprocessing_stats']['urdu_percentage']:.1f}%")
        print(f"\nContent Preview:")
        print(story['content_clean'][:500])
        print(f"\n{'='*80}")
        
        response = input("Quality OK? (y/n/skip): ")
        if response.lower() == 'n':
            print(f"FLAGGED: {story['id']}")
```

---

# Phase 1 Execution Guide

## Setup Commands

```bash
# 1. Create project structure
mkdir -p urdu-story-ai/{data/{raw,processed,metadata},src/{scraping,preprocessing,utils},config,scripts,logs}

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Create configuration files
# (Copy YAML configs from above into config/ directory)
```

## Scraping Execution

```bash
# Test individual scrapers
python scripts/run_scraper.py --source urdupoint --limit 10 --test

# Run full scraping
python scripts/run_scraper.py --all

# Check progress
python scripts/scraping_status.py
```

## Preprocessing Execution

```bash
# Run preprocessing pipeline
python scripts/run_preprocessing.py --input data/raw/all_stories.json --output data/processed/

# Generate statistics
python scripts/generate_statistics.py --corpus data/processed/stories.json --output data/processed/statistics.json

# Create vocabulary
python scripts/create_vocabulary.py --corpus data/processed/stories.json --output data/processed/vocabulary.txt

# Manual quality check
python scripts/manual_review.py --corpus data/processed/stories.json --sample 20
```

---

# Success Criteria Checklist

## Quantitative Metrics

- [ ] **500 stories** collected (target: 400-500)
- [ ] **>90% Urdu purity** across corpus
- [ ] **150K-300K words** total
- [ ] **<5% scraping failures**
- [ ] **0 Unicode errors**
- [ ] **Special tokens** correctly inserted in all stories
- [ ] **<5% duplicates** (similarity >95%)

## Qualitative Metrics

- [ ] Stories are **readable and coherent**
- [ ] **Diverse content** across sources
- [ ] **No HTML artifacts** in processed text
- [ ] **Proper Unicode rendering**
- [ ] **Logs comprehensive** and informative

---

# Risk Mitigation Strategies

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Website blocks scraper | Medium | High | Rotate user agents, add delays, use proxies if needed |
| Insufficient stories from source | Medium | Medium | Have 2-3 backup sources ready |
| Low quality text | Low | Medium | Strict validation, manual spot-checks |
| Unicode corruption | Low | High | Multiple encoding tests, validation at each step |
| Legal/ToS violations | Low | High | Check robots.txt, respect rate limits, personal use only |
| Selenium setup issues | Medium | Low | Fallback to requests-html or alternative sources |

---

# Timeline Summary

## Week 1: Setup & Initial Scraping
- **1**: Environment setup, dependencies, config files
- **2**: Base scraper implementation
- **3**: UrduPoint scraper (100 stories)
- **4**: Rekhta scraper (120 stories)
- **5**: Kitab Nagri + BBC scrapers (140 stories)
- **6**: UrduKahani scraper (140 stories)
- **7**: Scraper manager, consolidation

## Week 2: Preprocessing & Validation
- **8**: Testing, final scraping adjustments
- **9**: HTML cleaner + Text normalizer
- **10**: Language filter + Special tokens
- **11**: Complete preprocessing pipeline
- **12**: Validation & quality control
- **13**: Statistics generation
- **14**: Final output creation

## Week 3: Review & Handoff
- **15**: Manual quality review, documentation
- **16-17**: Buffer for issues, re-scraping if needed
- **18**: Final delivery, Phase 2 prep

---

# Deliverables Checklist

## Code Deliverables
- [ ] Complete scraping framework (all 5+ scrapers)
- [ ] Full preprocessing pipeline
- [ ] Validation & quality control modules
- [ ] Statistics generation scripts
- [ ] Comprehensive logging & error handling

## Data Deliverables
- [ ] `stories.json` - 400-500 processed stories with metadata
- [ ] `stories.txt` - Plain text corpus
- [ ] `stories_with_tokens.txt` - Training-ready corpus
- [ ] `vocabulary.txt` - Unique words with frequencies
- [ ] `statistics.json` - Corpus statistics
- [ ] `scraping_log.json` - Scraping history
- [ ] `failed_urls.json` - Failed scrapes log
- [ ] `quality_report.txt` - Human-readable report

## Documentation Deliverables
- [ ] Scraping execution guide
- [ ] Preprocessing guide
- [ ] Dataset statistics report
- [ ] Quality assurance checklist
- [ ] Phase 1 completion report

---

# Post-Phase 1: Handoff to Phase 2

## Ready for Phase 2 When:

1. ✅ Clean corpus file available (`stories_with_tokens.txt`)
2. ✅ Special tokens verified and documented
3. ✅ Statistics show quality targets met
4. ✅ Manual QA completed
5. ✅ All documentation finalized

## Input to Phase 2 (BPE Tokenizer Training):

**Primary Input File:**
- `data/processed/stories_with_tokens.txt`

**Supporting Files:**
- `data/processed/statistics.json` (for reference)
- `data/processed/vocabulary.txt` (optional, for analysis)

**Special Tokens to Register in Tokenizer:**
```python
SPECIAL_TOKENS = {
    'STORY_START': '\uE000',
    'STORY_END': '\uE001',
    'PARAGRAPH': '\uE002',
    'SENTENCE': '\uE003',  # If used
}
```

---

# Appendix: Troubleshooting Guide

## Common Issues & Solutions

### Issue 1: Website Blocking
**Symptoms:** 403 Forbidden, CAPTCHA, connection refused
**Solutions:**
- Increase delay between requests (3-5 seconds)
- Rotate user agents more frequently
- Use residential proxies (optional)
- Scrape during off-peak hours

### Issue 2: JavaScript Rendering
**Symptoms:** Missing content, empty pages
**Solutions:**
- Use Selenium instead of requests
- Enable headless browser
- Add wait times for page load
- Use requests-html as alternative

### Issue 3: Low Urdu Percentage
**Symptoms:** Stories failing language filter
**Solutions:**
- Adjust threshold (85% → 80%)
- Improve English sentence removal
- Better source selection
- Manual review of edge cases

### Issue 4: Unicode Errors
**Symptoms:** Encoding exceptions, garbled text
**Solutions:**
- Force UTF-8 encoding everywhere
- Use NFKC normalization
- Validate at each pipeline stage
- Log problematic characters

### Issue 5: Insufficient Stories
**Symptoms:** Can't reach 400-500 target
**Solutions:**
- Add backup sources (Jashn-e-Rekhta, Humsub)
- Relax validation criteria slightly
- Scrape additional categories
- Manual story collection for gaps

---

# Contact & Support

For issues during Phase 1 implementation:
1. Check logs in `logs/` directory
2. Review `failed_urls.json` for scraping issues
3. Examine `preprocessing_failures.json` for pipeline errors
4. Run validation scripts to identify problems

---

**END OF PHASE 1 IMPLEMENTATION PLAN**

This plan is ready for execution. Follow the timeline, use the provided code structures, and monitor progress with the success criteria.

