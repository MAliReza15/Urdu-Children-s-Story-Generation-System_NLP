from typing import Dict, Tuple, List

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
        if not text:
             return False, "Empty content"
             
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
        if token_stats.get('story_start') != 1:
            return False
        if token_stats.get('story_end') != 1:
            return False
        # Paragraphs can be 0 for short stories
        return True
    
    def detect_duplicate(self, text: str, existing_texts: List[str], 
                        threshold: float = 0.95) -> bool:
        """
        Detect if text is duplicate/near-duplicate.
        Simple exact match or high similarity check.
        For phase 1, we can use exact match or first N chars.
        """
        # Placeholder for complex similarity
        if text in existing_texts:
            return True
        return False
    
    def validate_unicode(self, text: str) -> bool:
        """Validate all characters are valid Unicode."""
        try:
            text.encode('utf-8')
            return True
        except UnicodeEncodeError:
            return False
