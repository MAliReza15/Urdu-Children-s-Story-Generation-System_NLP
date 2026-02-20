"""
Global configuration for Phase III language model.
"""

DATA_PATH = "Data/processed_stories.json"
VOCAB_PATH = "Data/vocab.json"
MERGES_PATH = "Data/merges.json"


MAX_GENERATION_LENGTH = 500
RANDOM_SEED = 42

# Sampling hyperparameters
TEMPERATURE = 0.8   # <1 = more deterministic, >1 = more creative
TOP_K = 50          # use top-k probable tokens for sampling
TOP_P = 0.9         # cumulative probability for nucleus (top-p) sampling