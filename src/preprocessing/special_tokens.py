import re
from typing import Dict

class SpecialTokens:
    """Manages special tokens for story structure"""
    
    # Unicode Private Use Area (U+E000 to U+F8FF)
    STORY_START = '\uE000'
    STORY_END = '\uE001'
    PARAGRAPH = '\uE002'
    SENTENCE = '\uE003'
    
    def __init__(self, config: Dict):
        self.config = config
        tokens = config.get('special_tokens', {})
        self.STORY_START = tokens.get('story_start', self.STORY_START)
        self.STORY_END = tokens.get('story_end', self.STORY_END)
        self.PARAGRAPH = tokens.get('paragraph', self.PARAGRAPH)
        self.SENTENCE = tokens.get('sentence', self.SENTENCE)
    
    def insert_story_markers(self, text: str) -> str:
        """Wrap entire story with start/end markers."""
        return f"{self.STORY_START}{text}{self.STORY_END}"
    
    def insert_paragraph_markers(self, text: str) -> str:
        """
        Insert PARAGRAPH token between paragraphs.
        """
        # Split by paragraph breaks (2+ newlines)
        paragraphs = re.split(r'\n\s*\n', text)
        
        # Join with PARAGRAPH token
        return self.PARAGRAPH.join(p.strip() for p in paragraphs if p.strip())
    
    def insert_sentence_markers(self, text: str) -> str:
        """
        Insert SENTENCE token between sentences.
        """
        # Split by Urdu sentence endings
        sentences = re.split(r'([۔؟!])', text)
        
        # Reconstruct
        result = []
        for i in range(0, len(sentences)-1, 2):
            if sentences[i].strip():
                result.append(sentences[i].strip() + sentences[i+1])
        
        # Handle last part if not captured by split group
        if len(sentences) % 2 != 0 and sentences[-1].strip():
             result.append(sentences[-1].strip())

        return self.SENTENCE.join(result)
    
    def insert_all_tokens(self, text: str, include_sentence: bool = False) -> str:
        """
        Insert all structural tokens.
        """
        # 1. Paragraphs first
        text = self.insert_paragraph_markers(text)
        
        # 2. Sentences (optional)
        if include_sentence:
            text = self.insert_sentence_markers(text)
        
        # 3. Story markers (wraps everything)
        text = self.insert_story_markers(text)
        
        return text
    
    def get_token_statistics(self, text: str) -> Dict:
        """Get statistics about token usage."""
        return {
            'story_start': text.count(self.STORY_START),
            'story_end': text.count(self.STORY_END),
            'paragraph': text.count(self.PARAGRAPH),
            'sentence': text.count(self.SENTENCE),
        }
