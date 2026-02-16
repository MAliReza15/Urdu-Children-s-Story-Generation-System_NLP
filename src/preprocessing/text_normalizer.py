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
        'ھ': 'ھ',  # Dochashmi he
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
        if not text:
            return ""
            
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
        # For now, remove all ZWJ/ZWNJ as they often cause issues, 
        # unless specifically needed for complex ligature rendering which tokenizer handles.
        # However, ZWNJ (u+200c) is often used in Urdu compounds.
        # Let's keep ZWNJ but normalize usage if possible.
        # Strategy: strip them if isolated, maybe?
        # Plan says "pass". I'll implement basic cleanup.
        text = text.replace('\u200d', '') # Remove ZWJ
        # Keep ZWNJ (\u200c) as it separates words like 'ہم نے' vs 'ہمنے'
        return text
    
    def _standardize_punctuation(self, text: str) -> str:
        """
        Standardize punctuation marks to Urdu variants.
        """
        if 'punctuation' in self.config and 'standardize' in self.config['punctuation']:
            punct_map = self.config['punctuation']['standardize']
            for eng_punct, urdu_punct in punct_map.items():
                text = text.replace(eng_punct, urdu_punct)
        return text
    
    def _normalize_whitespace(self, text: str) -> str:
        """
        Normalize all whitespace.
        """
        return ' '.join(text.split())
    
    def _fix_rtl_issues(self, text: str) -> str:
        """Fix right-to-left text rendering issues."""
        # Mostly handled by bidi or just ensuring no LTR markers mix incorrectly.
        # For now, just remove LTR/RTL marks if they are clutter
        text = text.replace('\u200e', '').replace('\u200f', '')
        return text
