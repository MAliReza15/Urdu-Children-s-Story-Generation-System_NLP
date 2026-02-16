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
        if not text:
            return ""
            
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
        soup = BeautifulSoup(text, 'html.parser')
        for script in soup(["script", "style"]):
            script.extract()
        return str(soup)
    
    @staticmethod
    def _extract_text_from_html(text: str) -> str:
        """Extract text using BeautifulSoup."""
        soup = BeautifulSoup(text, 'html.parser')
        return soup.get_text(separator=' ')
    
    @staticmethod
    def _clean_whitespace(text: str) -> str:
        """Normalize whitespace."""
        return ' '.join(text.split())
