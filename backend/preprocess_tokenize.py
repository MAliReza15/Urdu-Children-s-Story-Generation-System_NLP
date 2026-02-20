"""
Pre-tokenize all story datasets for all model configurations.
Run this once before starting the server to create tokenized data files.
Usage: python preprocess_tokenize.py
"""

import os
import json
import sys
from tokenizer.bpe_tokenizer import BPETokenizer
from Data.data_loader import load_corpus

# Import MODEL_CONFIGS from main.py
sys.path.insert(0, os.path.dirname(__file__))
from main import MODEL_CONFIGS


def tokenize_model(model_key: str, config: dict):
    """Tokenize stories for a specific model configuration."""
    vocab_path = config["vocab"]
    merges_path = config["merges"]
    data_path = config["data"]
    tokenized_path = config["tokenized"]
    
    print(f"\n[{model_key}] Processing: {config['label']}")
    print(f"  Vocab: {vocab_path}")
    print(f"  Data: {data_path}")
    print(f"  Output: {tokenized_path}")
    
    # Check if files exist
    if not os.path.exists(vocab_path):
        print(f"  ✗ Skipping: Vocab file not found: {vocab_path}")
        return False
    
    if not os.path.exists(merges_path):
        print(f"  ✗ Skipping: Merges file not found: {merges_path}")
        return False
    
    if not os.path.exists(data_path):
        print(f"  ✗ Skipping: Data file not found: {data_path}")
        return False
    
    # Check if already tokenized
    if os.path.exists(tokenized_path):
        print(f"  ⚠ Tokenized file already exists. Skipping...")
        return True
    
    try:
        # Load tokenizer
        print(f"  Loading tokenizer...")
        tokenizer = BPETokenizer(vocab_path, merges_path)
        
        # Load stories
        print(f"  Loading stories from {data_path}...")
        texts = load_corpus(data_path)
        print(f"  Found {len(texts)} stories")
        
        # Tokenize
        print(f"  Tokenizing stories...")
        tokenized = []
        for i, text in enumerate(texts):
            tokenized.append(tokenizer.encode(text))
            if (i + 1) % 100 == 0:
                print(f"    Progress: {i + 1}/{len(texts)} stories tokenized")
        
        # Save tokenized data
        print(f"  Saving tokenized data to {tokenized_path}...")
        os.makedirs(os.path.dirname(tokenized_path), exist_ok=True)
        with open(tokenized_path, "w", encoding="utf-8") as f:
            json.dump(tokenized, f, ensure_ascii=False, indent=2)
        
        print(f"  ✓ Successfully tokenized and saved {len(tokenized)} stories")
        return True
        
    except Exception as e:
        print(f"  ✗ Error: {str(e)}")
        return False


def main():
    print("="*70)
    print("PRE-TOKENIZING ALL MODEL CONFIGURATIONS")
    print("="*70)
    
    total = len(MODEL_CONFIGS)
    success = 0
    failed = 0
    skipped = 0
    
    for model_key, config in MODEL_CONFIGS.items():
        result = tokenize_model(model_key, config)
        if result is True:
            if os.path.exists(config["tokenized"]):
                success += 1
            else:
                skipped += 1
        else:
            failed += 1
    
    print("\n" + "="*70)
    print("PRE-TOKENIZATION COMPLETE")
    print("="*70)
    print(f"  ✓ Successfully tokenized: {success}/{total}")
    print(f"  ⚠ Already existed (skipped): {skipped}/{total}")
    print(f"  ✗ Failed: {failed}/{total}")
    print("="*70)
    
    if success + skipped == total:
        print("\n✅ All models are ready! You can now start the server.")
    else:
        print("\n⚠️  Some models failed. Check the errors above.")


if __name__ == "__main__":
    main()
