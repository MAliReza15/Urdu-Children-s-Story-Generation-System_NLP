from typing import Dict, List, Optional
import json
from pathlib import Path
import logging
from datetime import datetime
import yaml

from .html_cleaner import HTMLCleaner
from .text_normalizer import TextNormalizer
from .language_filter import LanguageFilter
from .special_tokens import SpecialTokens
from ..utils.validators import DataValidator

class PreprocessingPipeline:
    """
    Complete preprocessing pipeline for Urdu stories.
    """
    
    def __init__(self, config_path: str):
        """Initialize pipeline with configuration."""
        with open(config_path, 'r', encoding='utf-8') as f:
            full_config = yaml.safe_load(f)
            self.config = full_config['preprocessing']
            # Validator needs parts of config like validation thresholds which might be in preprocessing or separate.
            # In the plan, 'validation' section is top level in preprocessing_config?
            # Let's check config file I created.
            # In `preprocessing_config.yaml`, validation is at root level BUT indentation in plan implies it might be separate.
            # My created config has `validation` at root level.
            # So I need to pass the whole config or relevant parts to Validator.
            # The Validator expects specific keys.
            # Let's pass the whole loaded config to Validator if it matches structure.
            # My Validator expects: config['validation']['min_word_count'] etc.
            # My `preprocessing_config.yaml` has `validation` key. So passing `full_config` works if keys match.
            # Wait, `min_word_count` is in `scraping_config.yaml` in the plan (lines 191), BUT `validators.py` implementation in plan (lines 1447) says `config['validation']['min_word_count']`.
            # In `preprocessing_config.yaml`, I see `validation` section but it has `check_unicode_validity` etc.
            # `min_word_count` seems to be in `scraping_config`.
            # This is a small inconsistency in the plan or I need to merging configs.
            # For simplicity, I will use defaults or assume they are in preprocessing config too, or load both.
            # I'll stick to what I have in `preprocessing_config.yaml` which I created.
            # Checking `preprocessing_config.yaml` content I wrote...
            # It DOES NOT have min_word_count.
            # I should probably update `preprocessing_config.yaml` to include these or load them.
            # Or better, just hardcode defaults in Validator for now or ignore word count in Preprocessing if it was done in Scraping.
            # Plan says Validator is used in Pipeline.
            # I will add `min_word_count` to `preprocessing_config.yaml` implicitly or just update the file now.
            # Actually, I'll update `preprocessing_config.yaml` to include validation metrics needed by Validator.
            
            # Let's fix this dynamic: I'll load scraping config too if needed, OR just update Validator to use get() with defaults.
            pass
        
        # Re-reading config to ensure I have what I need.
        # I will inject the missing validation keys into the loaded config for Validator
        # or separate them.
        self.validation_config = full_config.get('validation', {})
        # Ensure min_word_count exists
        if 'min_word_count' not in self.validation_config:
             self.validation_config['min_word_count'] = 100
        if 'max_word_count' not in self.validation_config:
             self.validation_config['max_word_count'] = 5000
        if 'min_urdu_percentage' not in self.validation_config:
             self.validation_config['min_urdu_percentage'] = 85.0
             
        full_config['validation'] = self.validation_config

        # Initialize components
        self.html_cleaner = HTMLCleaner()
        self.normalizer = TextNormalizer(self.config)
        self.lang_filter = LanguageFilter(self.config)
        self.special_tokens = SpecialTokens(self.config)
        self.validator = DataValidator(full_config)
        
        # Statistics
        self.stats = {
            'total_processed': 0,
            'successful': 0,
            'failed': 0,
            'rejected_low_quality': 0,
            'rejected_language': 0,
            'failures': []
        }
        
        self.logger = logging.getLogger("PreprocessingPipeline")
        self.logger.setLevel(logging.INFO)
    
    def process_story(self, raw_story: Dict) -> Optional[Dict]:
        """
        Process a single story through the pipeline.
        """
        story_id = 'unknown'
        try:
            story_id = raw_story.get('id', 'unknown')
            # self.logger.info(f"Processing story: {story_id}")
            
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
                self.logger.debug(f"Story {story_id} rejected: language filter")
                self.stats['rejected_language'] += 1
                return None
            
            # Stage 4: Quality Validation
            is_valid, reason = self.validator.validate_content(content)
            if not is_valid:
                self.logger.debug(f"Story {story_id} rejected: {reason}")
                self.stats['rejected_low_quality'] += 1
                return None
            
            # Stage 5: Special Token Insertion
            content_with_tokens = self.special_tokens.insert_all_tokens(
                content, 
                include_sentence=False
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
        """
        input_file = Path(input_path)
        output_dir = Path(output_path)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        self.logger.info(f"Starting corpus processing: {input_path}")
        
        # Handle if input is a directory of JSONs or a single JSON list
        raw_stories = []
        if input_file.is_file():
            with open(input_file, 'r', encoding='utf-8') as f:
                raw_stories = json.load(f)
        elif input_file.is_dir():
             # Recursively find json files? Or just flat
             # Plan says "raw/urdupoint/..."
             # We might need to walk the directories
             for f in input_file.rglob("*.json"):
                 try:
                     with open(f, 'r', encoding='utf-8') as jf:
                         data = json.load(jf)
                         if isinstance(data, list):
                             raw_stories.extend(data)
                         else:
                             raw_stories.append(data)
                 except:
                     pass
        
        self.stats['total_processed'] = len(raw_stories)
        processed_stories = []
        
        self.logger.info(f"Loaded {len(raw_stories)} raw stories")
        
        # Process
        for i, raw_story in enumerate(raw_stories, 1):
            processed = self.process_story(raw_story)
            
            if processed:
                processed_stories.append(processed)
            
            if i % batch_size == 0:
                self.logger.info(f"Processed {i}/{len(raw_stories)} stories")
        
        # Save final
        self._save_final(processed_stories, output_dir)
        
        return self.stats

    def _save_final(self, stories: List[Dict], output_path: Path):
        """Save final processed corpus."""
        # Save as JSON
        json_path = output_path / 'stories.json'
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(stories, f, ensure_ascii=False, indent=2)
        
        # Save as plain text
        txt_path = output_path / 'stories.txt'
        with open(txt_path, 'w', encoding='utf-8') as f:
            for story in stories:
                f.write(story['content_clean'] + '\n\n')
        
        # Save as text with tokens
        tokens_path = output_path / 'stories_with_tokens.txt'
        with open(tokens_path, 'w', encoding='utf-8') as f:
            for story in stories:
                f.write(story['content_with_tokens'] + '\n')
