import argparse
import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from src.preprocessing.pipeline import PreprocessingPipeline

def main():
    parser = argparse.ArgumentParser(description="Run Urdu Story Preprocessing")
    parser.add_argument('--config', type=str, default='config/preprocessing_config.yaml', help='Path to config file')
    parser.add_argument('--input', type=str, required=True, help='Input directory (raw data) or file')
    parser.add_argument('--output', type=str, default='data/processed', help='Output directory')
    
    args = parser.parse_args()
    
    pipeline = PreprocessingPipeline(args.config)
    pipeline.process_corpus(args.input, args.output)
    
    print("Preprocessing complete.")

if __name__ == "__main__":
    main()
