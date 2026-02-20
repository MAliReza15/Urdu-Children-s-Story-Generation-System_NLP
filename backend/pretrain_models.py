"""
Pre-train all n-gram models (trigram, 5gram, 7gram) for all vocab/merges combinations.
This script should be run once before starting the FastAPI server to reduce startup overhead.

Usage: python pretrain_models.py
"""

import os
import sys
import json
from concurrent.futures import ThreadPoolExecutor, as_completed

from Data.data_loader import load_corpus
from tokenizer.bpe_tokenizer import BPETokenizer
from models.model_factory import get_model

# Import from main.py (run from backend directory)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from main import MODEL_CONFIGS, load_tokenized_data


def train_and_save_model(model_key: str, ngram_type: str, config: dict):
    """Train a single model and save it to disk."""
    import sys
    
    cache_key = f"{model_key}_{ngram_type}"
    model_path = config["models"][ngram_type]
    
    try:
        print(f"[{cache_key}] Starting training...", flush=True)
        sys.stdout.flush()
        
        # Load tokenizer
        vocab_path = config["vocab"]
        merges_path = config["merges"]
        tokenized_path = config["tokenized"]
        data_path = config["data"]
        
        if not os.path.exists(vocab_path):
            raise FileNotFoundError(f"Vocab file not found: {vocab_path}")
        if not os.path.exists(merges_path):
            raise FileNotFoundError(f"Merges file not found: {merges_path}")
        
        tokenizer = BPETokenizer(vocab_path, merges_path)
        
        # Load pre-tokenized data (or tokenize if needed)
        print(f"[{cache_key}] Loading tokenized data...", flush=True)
        sys.stdout.flush()
        tokenized = load_tokenized_data(tokenized_path, tokenizer, data_path)
        
        # Train model
        print(f"[{cache_key}] Training {ngram_type} model on {len(tokenized)} stories...", flush=True)
        sys.stdout.flush()
        model = get_model(ngram_type)
        model.train(tokenized)
        
        # Save model
        print(f"[{cache_key}] Saving model to {model_path}...", flush=True)
        sys.stdout.flush()
        model.save(model_path)
        
        vocab_size = len(tokenizer.id_to_token)
        print(f"[{cache_key}] ✓ Successfully trained and saved (vocab: {vocab_size})", flush=True)
        sys.stdout.flush()
        
        return cache_key, None
    except Exception as e:
        print(f"[{cache_key}] ✗ Failed: {str(e)}", flush=True)
        sys.stdout.flush()
        return cache_key, str(e)


def main():
    """Pre-train all models for all combinations."""
    print("\n" + "="*70)
    print("🚀 PRE-TRAINING ALL N-GRAM MODELS")
    print("="*70)
    print()
    
    ngram_types = ["trigram", "5gram", "7gram"]
    model_keys = list(MODEL_CONFIGS.keys())
    
    total_models = len(model_keys) * len(ngram_types)
    
    print(f"📦 Found {len(model_keys)} vocab models × {len(ngram_types)} ngram types = {total_models} models to train")
    print(f"⚙️  Using {min(total_models, 4)} parallel workers")
    print()
    
    # Create models directory if it doesn't exist
    os.makedirs("Data/models", exist_ok=True)
    
    # Train all models in parallel
    with ThreadPoolExecutor(max_workers=min(total_models, 4)) as executor:
        futures = {}
        for key in model_keys:
            for ngram in ngram_types:
                config = MODEL_CONFIGS[key]
                futures[executor.submit(train_and_save_model, key, ngram, config)] = f"{key}_{ngram}"
        
        trained = 0
        failed = 0
        
        for i, future in enumerate(as_completed(futures), 1):
            cache_key, error = future.result()
            if error is None:
                trained += 1
            else:
                failed += 1
            
            # Progress update
            print(f"📊 Progress: {i}/{total_models} models processed ({trained} trained, {failed} failed)", flush=True)
            sys.stdout.flush()
    
    print("\n" + "="*70)
    print(f"✅ PRE-TRAINING COMPLETE")
    print(f"   ✓ Trained: {trained}/{total_models}")
    if failed > 0:
        print(f"   ✗ Failed: {failed}/{total_models}")
    print("="*70)
    print("\n💡 You can now start the FastAPI server - models will load instantly!")
    print()


if __name__ == "__main__":
    main()
