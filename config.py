"""
Global configuration for Phase III language model.
"""

DATA_PATH = "Data/processed_stories.json"
VOCAB_PATH = "Data/vocab.json"
MERGES_PATH = "Data/merges.json"

# Interpolation weights
LAMBDA_UNI = 0.1
LAMBDA_BI = 0.3
LAMBDA_TRI = 0.6

MAX_GENERATION_LENGTH = 500
RANDOM_SEED = 42
