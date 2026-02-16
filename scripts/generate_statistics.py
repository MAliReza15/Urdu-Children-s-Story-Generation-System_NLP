import argparse
import json
from pathlib import Path
from collections import Counter
import sys

class CorpusAnalyzer:
    """Analyzes and generates statistics for the corpus"""
    
    def __init__(self, corpus_path: str):
        self.corpus_path = Path(corpus_path)
        self.stories = self._load_stories()
        
    def _load_stories(self):
        """Load processed stories."""
        # Check if it's a file or dir
        if self.corpus_path.is_file():
             with open(self.corpus_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        elif (self.corpus_path / 'stories.json').exists():
             with open(self.corpus_path / 'stories.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        return []

    def generate_statistics(self):
        """Generate comprehensive statistics."""
        if not self.stories:
            return {"error": "No stories found"}
            
        stats = {
            'overview': self._overview_stats(),
            'sources': self._source_distribution(),
            'quality_metrics': self._quality_metrics(),
            'vocabulary': self._vocabulary_stats(),
            'length_distribution': self._length_distribution(),
        }
        
        return stats
    
    def _overview_stats(self):
        """Basic overview statistics."""
        total_words = sum(s['preprocessing_stats']['word_count'] for s in self.stories)
        total_chars = sum(s['preprocessing_stats']['char_count'] for s in self.stories)
        
        return {
            'total_stories': len(self.stories),
            'total_words': total_words,
            'total_characters': total_chars,
            'average_story_length': total_words / len(self.stories) if self.stories else 0,
            'average_char_length': total_chars / len(self.stories) if self.stories else 0,
        }
    
    def _source_distribution(self):
        """Distribution across sources."""
        sources = Counter(s.get('source', 'unknown') for s in self.stories)
        return dict(sources)
    
    def _quality_metrics(self):
        """Quality-related metrics."""
        urdu_percentages = [
            s['preprocessing_stats']['urdu_percentage'] 
            for s in self.stories
        ]
        
        if not urdu_percentages:
            return {}

        return {
            'average_urdu_percentage': sum(urdu_percentages) / len(urdu_percentages),
            'min_urdu_percentage': min(urdu_percentages),
            'max_urdu_percentage': max(urdu_percentages),
        }
    
    def _vocabulary_stats(self):
        """Vocabulary statistics."""
        # Combine all text
        # Be careful with memory for large corpora
        # For 500 stories it's fine.
        all_text = ' '.join(s['content_clean'] for s in self.stories)
        words = all_text.split()
        
        unique_words = set(words)
        unique_chars = set(all_text)
        
        return {
            'total_words': len(words),
            'unique_words': len(unique_words),
            'unique_characters': len(unique_chars),
            'vocabulary_richness': len(unique_words) / len(words) if words else 0,
        }
    
    def _length_distribution(self):
        """Story length distribution buckets."""
        lengths = [s['preprocessing_stats']['word_count'] for s in self.stories]
        # Simple stats
        if not lengths:
            return {}
            
        return {
            'min': min(lengths),
            'max': max(lengths),
            # 'buckets': ... (could implement buckets if needed)
        }

def main():
    parser = argparse.ArgumentParser(description="Generate Corpus Statistics")
    parser.add_argument('--corpus', type=str, required=True, help='Path to processed stories.json or directory')
    parser.add_argument('--output', type=str, default='data/metadata/statistics.json', help='Output file for stats')
    
    args = parser.parse_args()
    
    analyzer = CorpusAnalyzer(args.corpus)
    stats = analyzer.generate_statistics()
    
    # Save stats
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(stats, f, indent=2, ensure_ascii=False)
        
    print(f"Statistics saved to {output_path}")
    if 'error' in stats:
        print(f"Error: {stats['error']}")
    else:
        print(json.dumps(stats['overview'], indent=2))

if __name__ == "__main__":
    main()
