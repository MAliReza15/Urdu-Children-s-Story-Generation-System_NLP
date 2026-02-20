"""
FastAPI backend for Urdu story generation.
Run from backend directory: uvicorn main:app --reload
"""

import os
import random
import json
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from config import DATA_PATH, RANDOM_SEED, MERGES_PATH, VOCAB_PATH
from Data.data_loader import load_corpus
from tokenizer.bpe_tokenizer import BPETokenizer
from models.model_factory import get_model
from generation.generator import StoryGenerator


# ---------------------------------------------------------------------------
# Model configurations (vocab/merges combinations)
# ---------------------------------------------------------------------------

MODEL_CONFIGS = {
    "default": {
        "vocab": "Data/vocab.json",
        "merges": "Data/merges.json",
        "data": "Data/processed_stories.json",
        "tokenized": "Data/tokenized_default.json",
        "models": {
            "trigram": "Data/models/default_trigram.json",
            "5gram": "Data/models/default_5gram.json",
            "7gram": "Data/models/default_7gram.json",
        },
        "label": "Default (vocab.json)"
    },
    "500_250": {
        "vocab": "Data/vocab_500_250.json",
        "merges": "Data/merges_500_250.json",
        "data": "Data/processed_stories_500.json",
        "tokenized": "Data/tokenized_500_250.json",
        "models": {
            "trigram": "Data/models/500_250_trigram.json",
            "5gram": "Data/models/500_250_5gram.json",
            "7gram": "Data/models/500_250_7gram.json",
        },
        "label": "500 stories, 250 vocab"
    },
    "500_1000": {
        "vocab": "Data/vocab_500_1000.json",
        "merges": "Data/merges_500_1000.json",
        "data": "Data/processed_stories_500.json",
        "tokenized": "Data/tokenized_500_1000.json",
        "models": {
            "trigram": "Data/models/500_1000_trigram.json",
            "5gram": "Data/models/500_1000_5gram.json",
            "7gram": "Data/models/500_1000_7gram.json",
        },
        "label": "500 stories, 1000 vocab"
    },
    "500_5000": {
        "vocab": "Data/vocab_500_5000.json",
        "merges": "Data/merges_500_5000.json",
        "data": "Data/processed_stories_500.json",
        "tokenized": "Data/tokenized_500_5000.json",
        "models": {
            "trigram": "Data/models/500_5000_trigram.json",
            "5gram": "Data/models/500_5000_5gram.json",
            "7gram": "Data/models/500_5000_7gram.json",
        },
        "label": "500 stories, 5000 vocab"
    },
    "1000_250": {
        "vocab": "Data/vocab_1000_250.json",
        "merges": "Data/merges_1000_250.json",
        "data": "Data/processed_stories_1000.json",
        "tokenized": "Data/tokenized_1000_250.json",
        "models": {
            "trigram": "Data/models/1000_250_trigram.json",
            "5gram": "Data/models/1000_250_5gram.json",
            "7gram": "Data/models/1000_250_7gram.json",
        },
        "label": "1000 stories, 250 vocab"
    },
    "all_250": {
        "vocab": "Data/vocab_all_250.json",
        "merges": "Data/merges_all_250.json",
        "data": "Data/processed_stories.json",
        "tokenized": "Data/tokenized_all_250.json",
        "models": {
            "trigram": "Data/models/all_250_trigram.json",
            "5gram": "Data/models/all_250_5gram.json",
            "7gram": "Data/models/all_250_7gram.json",
        },
        "label": "All stories, 250 vocab"
    },
    "all_1000": {
        "vocab": "Data/vocab_all_1000.json",
        "merges": "Data/merges_all_1000.json",
        "data": "Data/processed_stories.json",
        "tokenized": "Data/tokenized_all_1000.json",
        "models": {
            "trigram": "Data/models/all_1000_trigram.json",
            "5gram": "Data/models/all_1000_5gram.json",
            "7gram": "Data/models/all_1000_7gram.json",
        },
        "label": "All stories, 1000 vocab"
    },
    "all_5000": {
        "vocab": "Data/vocab_all_5000.json",
        "merges": "Data/merges_all_5000.json",
        "data": "Data/processed_stories.json",
        "tokenized": "Data/tokenized_all_5000.json",
        "models": {
            "trigram": "Data/models/all_5000_trigram.json",
            "5gram": "Data/models/all_5000_5gram.json",
            "7gram": "Data/models/all_5000_7gram.json",
        },
        "label": "All stories, 5000 vocab"
    },
}

# ---------------------------------------------------------------------------
# Config (env overrides)
# ---------------------------------------------------------------------------

VOCAB_PATH_ENV = os.environ.get("VOCAB_PATH", VOCAB_PATH)
MERGES_PATH_ENV = os.environ.get("MERGES_PATH", MERGES_PATH)
DATA_PATH_ENV = os.environ.get("DATA_PATH", DATA_PATH)
MODEL_NAME_ENV = os.environ.get("MODEL_NAME", "trigram")
DEFAULT_MODEL_KEY = os.environ.get("DEFAULT_MODEL_KEY", "default")


# ---------------------------------------------------------------------------
# App state (loaded at startup)
# ---------------------------------------------------------------------------

class AppState:
    generators: dict[str, StoryGenerator] = {}  # key: f"{model_key}_{ngram_type}"
    tokenizers: dict[str, BPETokenizer] = {}  # key: model_key
    default_model_key: str = "default"


state = AppState()


def load_tokenized_data(tokenized_path: str, tokenizer: BPETokenizer, data_path: str):
    """Load pre-tokenized data or create it if it doesn't exist."""
    import sys
    
    # Check if pre-tokenized file exists
    if os.path.exists(tokenized_path):
        print(f"  Loading pre-tokenized data from {tokenized_path}...", flush=True)
        sys.stdout.flush()
        with open(tokenized_path, "r", encoding="utf-8") as f:
            tokenized = json.load(f)
        print(f"  ✓ Loaded {len(tokenized)} pre-tokenized stories", flush=True)
        sys.stdout.flush()
        return tokenized
    
    # If not exists, tokenize and save
    print(f"  Pre-tokenized file not found. Tokenizing stories from {data_path}...", flush=True)
    sys.stdout.flush()
    texts = load_corpus(data_path)
    print(f"  Tokenizing {len(texts)} stories...", flush=True)
    sys.stdout.flush()
    
    tokenized = []
    for i, text in enumerate(texts):
        tokenized.append(tokenizer.encode(text))
        if (i + 1) % 100 == 0:
            print(f"  Progress: {i + 1}/{len(texts)} stories tokenized", flush=True)
            sys.stdout.flush()
    
    # Save tokenized data for future use
    print(f"  Saving tokenized data to {tokenized_path}...", flush=True)
    sys.stdout.flush()
    with open(tokenized_path, "w", encoding="utf-8") as f:
        json.dump(tokenized, f, ensure_ascii=False, indent=2)
    print(f"  ✓ Saved tokenized data for future use", flush=True)
    sys.stdout.flush()
    
    return tokenized


def load_model_and_generator(model_key: str = None, ngram_type: str = "trigram", lock: threading.Lock = None):
    """Load tokenizer, load pre-tokenized data, train model, create generator (cached after first load)."""
    import sys
    
    if model_key is None:
        model_key = DEFAULT_MODEL_KEY
    
    # Create composite cache key
    cache_key = f"{model_key}_{ngram_type}"
    
    # Return cached if already loaded (thread-safe check)
    if lock:
        lock.acquire()
    try:
        if cache_key in state.generators:
            generator = state.generators[cache_key]
            tokenizer = state.tokenizers[model_key]  # Tokenizer is shared per vocab
            return generator, tokenizer
    finally:
        if lock:
            lock.release()
    
    # Validate model key
    if model_key not in MODEL_CONFIGS:
        raise ValueError(f"Unknown model key: {model_key}. Available: {list(MODEL_CONFIGS.keys())}")
    
    # Validate ngram type
    if ngram_type not in ["trigram", "5gram", "7gram"]:
        raise ValueError(f"Unknown ngram type: {ngram_type}. Available: trigram, 5gram, 7gram")
    
    config = MODEL_CONFIGS[model_key]
    random.seed(RANDOM_SEED)

    vocab_path = config["vocab"]
    merges_path = config["merges"]
    data_path = config["data"]
    tokenized_path = config["tokenized"]
    
    # Check if files exist
    if not os.path.exists(vocab_path):
        raise FileNotFoundError(f"Vocab file not found: {vocab_path}")
    if not os.path.exists(merges_path):
        raise FileNotFoundError(f"Merges file not found: {merges_path}")
    if not os.path.exists(data_path):
        raise FileNotFoundError(f"Data file not found: {data_path}")

    # Load tokenizer (cache per vocab_key)
    if lock:
        lock.acquire()
    try:
        if model_key not in state.tokenizers:
            print(f"[{model_key}] Loading tokenizer from {vocab_path}...", flush=True)
            sys.stdout.flush()
            state.tokenizers[model_key] = BPETokenizer(vocab_path, merges_path)
        tokenizer = state.tokenizers[model_key]
    finally:
        if lock:
            lock.release()
    
    # Try to load pre-trained model, otherwise train and save
    model_path = config["models"].get(ngram_type)
    
    if model_path and os.path.exists(model_path):
        print(f"[{cache_key}] Loading pre-trained {ngram_type} model from {model_path}...", flush=True)
        sys.stdout.flush()
        from models.ngram_llm import NGramLanguageModel
        model = NGramLanguageModel.load(model_path)
    else:
        # Load pre-tokenized data (or tokenize and save if first time)
        print(f"[{cache_key}] Loading tokenized data...", flush=True)
        sys.stdout.flush()
        tokenized = load_tokenized_data(tokenized_path, tokenizer, data_path)

        print(f"[{cache_key}] Training {ngram_type} model on {len(tokenized)} stories...", flush=True)
        sys.stdout.flush()
        model = get_model(ngram_type)
        model.train(tokenized)
        
        # Save trained model for future use
        if model_path:
            print(f"[{cache_key}] Saving trained model to {model_path}...", flush=True)
            sys.stdout.flush()
            model.save(model_path)
            print(f"[{cache_key}] ✓ Model saved", flush=True)
            sys.stdout.flush()

    generator = StoryGenerator(model, tokenizer)
    
    # Cache for future use (thread-safe)
    if lock:
        lock.acquire()
    try:
        state.generators[cache_key] = generator
    finally:
        if lock:
            lock.release()
    
    return generator, tokenizer


def load_single_model(model_key: str, ngram_type: str, lock: threading.Lock):
    """Load a single model (for parallel loading)."""
    import sys
    try:
        label = MODEL_CONFIGS[model_key]["label"]
        cache_key = f"{model_key}_{ngram_type}"
        print(f"[{cache_key}] Starting to load: {label} ({ngram_type})", flush=True)
        sys.stdout.flush()
        
        load_model_and_generator(model_key, ngram_type, lock)
        
        if model_key in state.tokenizers:
            vocab_size = len(state.tokenizers[model_key].id_to_token)
            print(f"[{cache_key}] ✓ Successfully loaded: {label} ({ngram_type}, vocab: {vocab_size})", flush=True)
        else:
            print(f"[{cache_key}] ✓ Successfully loaded: {label} ({ngram_type})", flush=True)
        sys.stdout.flush()
        return cache_key, None
    except Exception as e:
        cache_key = f"{model_key}_{ngram_type}"
        print(f"[{cache_key}] ✗ Failed to load: {str(e)}", flush=True)
        sys.stdout.flush()
        return cache_key, str(e)


def preload_all_models():
    """Preload only 'all_*' trigram models in parallel; others load on-demand."""
    import sys
    
    print("\n" + "="*70, flush=True)
    print("🚀 PRELOADING SELECTED MODELS IN PARALLEL", flush=True)
    print("="*70, flush=True)
    sys.stdout.flush()
    
    lock = threading.Lock()
    # Only preload models whose keys contain 'all' (e.g. all_250, all_1000, all_5000)
    model_keys = [key for key in MODEL_CONFIGS.keys() if "all" in key]
    # Only preload trigram; 5-gram and 7-gram will load lazily on first request
    ngram_types = ["trigram"]
    total = len(model_keys) * len(ngram_types)
    
    print(f"📦 Found {len(model_keys)} vocab models × {len(ngram_types)} ngram types = {total} models to load", flush=True)
    print(f"⚙️  Using {min(total, 4)} parallel workers\n", flush=True)
    sys.stdout.flush()
    
    # Use ThreadPoolExecutor to load models in parallel
    with ThreadPoolExecutor(max_workers=min(total, 4)) as executor:
        futures = {}
        for key in model_keys:
            for ngram in ngram_types:
                futures[executor.submit(load_single_model, key, ngram, lock)] = f"{key}_{ngram}"
        
        loaded = 0
        failed = 0
        
        for i, future in enumerate(as_completed(futures), 1):
            cache_key, error = future.result()
            if error is None:
                loaded += 1
            else:
                failed += 1
            
            # Progress update
            print(f"📊 Progress: {i}/{total} models processed ({loaded} loaded, {failed} failed)", flush=True)
            sys.stdout.flush()
        
        print("\n" + "="*70, flush=True)
        print(f"✅ MODEL LOADING COMPLETE", flush=True)
        print(f"   ✓ Loaded: {loaded}/{total} models", flush=True)
        if failed > 0:
            print(f"   ✗ Failed: {failed}/{total}", flush=True)
        print("="*70 + "\n", flush=True)
        sys.stdout.flush()


@asynccontextmanager
async def lifespan(app: FastAPI):
    import sys
    print("\n" + "="*70, flush=True)
    print("🔧 APPLICATION STARTUP", flush=True)
    print("="*70, flush=True)
    sys.stdout.flush()
    
    # Preload all models in parallel threads at startup
    preload_all_models()
    state.default_model_key = DEFAULT_MODEL_KEY
    
    print("✅ Application startup complete. Ready to serve requests!\n", flush=True)
    sys.stdout.flush()
    
    yield
    
    # cleanup if needed
    print("\n🛑 Shutting down...", flush=True)
    sys.stdout.flush()
    state.generators.clear()
    state.tokenizers.clear()


# ---------------------------------------------------------------------------
# FastAPI app
# ---------------------------------------------------------------------------

app = FastAPI(
    title="Urdu Story Generation API",
    description="Generate Urdu children's stories using N-gram language model + BPE tokenizer",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Request/Response models
# ---------------------------------------------------------------------------

class GenerateRequest(BaseModel):
    prompt: str | None = Field(None, description="Optional text to seed generation (last tokens used as context)")
    max_length: int | None = Field(None, ge=1, le=2000, description="Max tokens to generate")
    temperature: float | None = Field(None, ge=0.01, le=2.0, description="Sampling temperature")
    top_k: int | None = Field(None, ge=1, le=500, description="Top-k sampling")
    model_key: str | None = Field(None, description="Model key (e.g., '500_250', 'all_1000'). Uses default if not specified.")
    ngram_type: str | None = Field("trigram", description="N-gram model type: 'trigram', '5gram', or '7gram'")


class GenerateResponse(BaseModel):
    story: str


class InfoResponse(BaseModel):
    model: str
    vocab_size: int
    status: str = "ready"
    available_models: dict[str, str] = {}


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/api/models")
def list_models():
    """List all available model configurations."""
    return {
        "models": {key: config["label"] for key, config in MODEL_CONFIGS.items()},
        "default": DEFAULT_MODEL_KEY,
    }


@app.get("/", response_model=InfoResponse)
@app.get("/api/info", response_model=InfoResponse)
def info():
    if not state.generators:
        raise HTTPException(status_code=503, detail="No models loaded")
    
    default_gen = state.generators.get(state.default_model_key)
    if default_gen is None:
        raise HTTPException(status_code=503, detail="Default model not loaded")
    
    default_tokenizer = state.tokenizers.get(state.default_model_key)
    return InfoResponse(
        model=MODEL_CONFIGS.get(state.default_model_key, {}).get("label", state.default_model_key),
        vocab_size=len(default_tokenizer.id_to_token) if default_tokenizer else 0,
        status="ready",
        available_models={key: config["label"] for key, config in MODEL_CONFIGS.items()},
    )


@app.post("/api/generate", response_model=GenerateResponse)
def generate(req: GenerateRequest):
    # Determine which model to use
    model_key = req.model_key or state.default_model_key
    ngram_type = req.ngram_type or "trigram"
    
    if model_key not in MODEL_CONFIGS:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown model key: {model_key}. Available: {list(MODEL_CONFIGS.keys())}"
        )
    
    if ngram_type not in ["trigram", "5gram", "7gram"]:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown ngram_type: {ngram_type}. Available: trigram, 5gram, 7gram"
        )
    
    cache_key = f"{model_key}_{ngram_type}"
    
    # Get model from cache or load on-demand
    if cache_key not in state.generators:
        # Load on-demand if not preloaded
        try:
            load_model_and_generator(model_key, ngram_type)
        except FileNotFoundError as e:
            raise HTTPException(status_code=404, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error loading model: {str(e)}")
    
    generator = state.generators[cache_key]
    tokenizer = state.tokenizers[model_key]

    model = generator.model
    n = model.n

    # Start tokens: from prompt if provided and long enough, else EOT padding
    if req.prompt and req.prompt.strip():
        try:
            ids = tokenizer.encode(req.prompt.strip())
            if len(ids) >= n - 1:
                start_tokens = ids[-(n - 1) :]
            else:
                start_tokens = [tokenizer.eot_id] * (n - 1)
        except Exception:
            start_tokens = [tokenizer.eot_id] * (n - 1)
    else:
        start_tokens = [tokenizer.eot_id] * (n - 1)

    story = generator.generate(
        start_tokens,
        max_length=req.max_length,
        temperature=req.temperature,
        top_k=req.top_k,
    )

    return GenerateResponse(story=story)
