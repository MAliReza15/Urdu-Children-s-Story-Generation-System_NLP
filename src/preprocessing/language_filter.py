import re
from langdetect import detect
from typing import Dict, Tuple

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
        if not text:
            return ""
            
        # 1. Check overall Urdu percentage
        urdu_pct = self.calculate_urdu_percentage(text)
        if urdu_pct < self.min_urdu_percentage:
            return ""  # Reject entire text
        
        # 2. Remove English sentences
        text = self._remove_english_sentences(text)
        
        # 3. Remove standalone English words
        text = self._remove_english_words(text)
        
        # 4. Remove Arabic-only paragraphs (keep Urdu-Arabic mix) -- Skipping for Phase 1 as it's complex 
        # to distinguish without deep linguistic analysis, and Urdu shares script.
        # self._filter_arabic_only(text)
        
        # 5. Final validation
        final_pct = self.calculate_urdu_percentage(text)
        if final_pct < self.min_urdu_percentage:
            return ""
        
        return text
    
    def calculate_urdu_percentage(self, text: str) -> float:
        """
        Calculate percentage of Urdu characters.
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
        """
        # Split by Urdu sentence delimiter (۔)
        sentences = text.split('۔')
        cleaned_sentences = []
        
        for sent in sentences:
            if not sent.strip():
                continue
            
            # fast check: if > 50% latin chars, remove
            latin_chars = sum(1 for c in sent if 'a' <= c.lower() <= 'z')
            total = len(sent.strip())
            if total > 0 and (latin_chars / total) > 0.5:
                continue
            
            cleaned_sentences.append(sent)
            
        return '۔'.join(cleaned_sentences) + ('۔' if text.endswith('۔') else '')
    
    def _remove_english_words(self, text: str) -> str:
        """
        Remove standalone English words using regex.
        Keep numbers in Urdu context.
        """
        if self.config['cleaning']['remove_english_words']:
            # Pattern: English words (but preserve Urdu)
            # Remove words encoded in ASCII
            pattern = r'\b[a-zA-Z]+\b'
            text = re.sub(pattern, '', text)
        return text
    
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
