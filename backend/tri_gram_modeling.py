"""
===============================================================================
PHASE III — TRIGRAM LANGUAGE MODEL
===============================================================================

Author: Phase III Implementation (Software Engineering Version)

DESCRIPTION
-----------
This module implements a fully modular Trigram Language Model trained on
Urdu stories tokenized using a custom BPE tokenizer (Phase II).

The design emphasizes:

    • Clean architecture
    • Upgradeability
    • Separation of concerns
    • Reusability for future NLP models

FEATURES
--------
✓ Loads processed stories
✓ Uses existing BPE tokenizer outputs
✓ Builds Unigram / Bigram / Trigram counts
✓ Maximum Likelihood Estimation (MLE)
✓ Linear Interpolation smoothing
✓ Probabilistic text generation
✓ Stops generation at <EOT>

FUTURE EXTENSIONS (No rewrite required)
---------------------------------------
• Perplexity evaluation
• Temperature sampling
• Top-k / nucleus sampling
• Neural language model replacement
• 4-gram or N-gram generalization

===============================================================================
"""

import json
import random
from collections import defaultdict
from typing import List, Dict, Tuple


# =============================================================================
# CONFIGURATION
# =============================================================================

DATA_PATH = "Data/processed_stories.json"
VOCAB_PATH = "Data/vocab.json"
MERGES_PATH = "Data/merges.json"

# Interpolation weights (must sum to 1)
LAMBDA_UNI = 0.1
LAMBDA_BI = 0.3
LAMBDA_TRI = 0.6

MAX_GENERATION_LENGTH = 500
RANDOM_SEED = 42


# =============================================================================
# TOKENIZER ADAPTER (CONNECTS PHASE II TOKENIZER TO PHASE III)
# =============================================================================

SPECIAL_TOKENS = {"<EOT>", "<EOS>", "<EOP>"}


class BPETokenizer:
    """
    Adapter class that converts text → token IDs using
    vocab.json and merges.json produced in Phase II.

    NOTE:
    We reuse your character tokenizer logic and sequentially
    apply learned merges.
    """

    def __init__(self, vocab_path: str, merges_path: str):
        # Load vocab
        with open(vocab_path, "r", encoding="utf-8") as f:
            raw_vocab = json.load(f)

        # keys stored as strings → convert to int
        self.id_to_token = {int(k): v for k, v in raw_vocab.items()}
        self.token_to_id = {v: k for k, v in self.id_to_token.items()}

        # Load merges
        with open(merges_path, "r", encoding="utf-8") as f:
            self.merges = json.load(f)

        self.eot_id = self.token_to_id["<EOT>"]

    # ---------------------------------------------------------------------

    def tokenize_text(self, text: str) -> List[str]:
        """Split text into characters while preserving special tokens."""
        tokens = []
        i = 0

        while i < len(text):
            matched = False
            for st in SPECIAL_TOKENS:
                if text[i:i + len(st)] == st:
                    tokens.append(st)
                    i += len(st)
                    matched = True
                    break

            if not matched:
                tokens.append(text[i])
                i += 1

        return tokens

    # ---------------------------------------------------------------------

    def encode(self, text: str) -> List[int]:
        """
        Convert text into BPE token IDs using learned merges.
        """

        tokens = self.tokenize_text(text)
        token_ids = [self.token_to_id[t] for t in tokens]

        # Apply merges sequentially
        for a, b, new_id, _ in self.merges:
            i = 0
            merged = []

            while i < len(token_ids):
                if (
                    i < len(token_ids) - 1
                    and token_ids[i] == a
                    and token_ids[i + 1] == b
                ):
                    merged.append(new_id)
                    i += 2
                else:
                    merged.append(token_ids[i])
                    i += 1

            token_ids = merged

        return token_ids


# =============================================================================
# DATA LOADING
# =============================================================================

def load_corpus(path: str) -> List[str]:
    """Load processed Urdu stories."""
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    return [story["content"] for story in data]


# =============================================================================
# N-GRAM LANGUAGE MODEL
# =============================================================================

class TrigramLanguageModel:
    """
    Statistical trigram language model with interpolation smoothing.
    """

    def __init__(self):
        self.unigram = defaultdict(int)
        self.bigram = defaultdict(int)
        self.trigram = defaultdict(int)

        self.total_tokens = 0

    # -----------------------------------------------------------------

    def train(self, tokenized_corpus: List[List[int]]):
        """
        Build n-gram counts from tokenized corpus.
        """

        for tokens in tokenized_corpus:

            for i in range(len(tokens)):

                self.unigram[(tokens[i],)] += 1
                self.total_tokens += 1

                if i >= 1:
                    self.bigram[(tokens[i - 1], tokens[i])] += 1

                if i >= 2:
                    self.trigram[(tokens[i - 2], tokens[i - 1], tokens[i])] += 1

        print("Training complete.")
        print(f"Total tokens: {self.total_tokens}")
        print(f"Unique trigrams: {len(self.trigram)}")

    # -----------------------------------------------------------------

    def interpolated_probability(
        self,
        w1: int,
        w2: int,
        w3: int,
        l1=LAMBDA_UNI,
        l2=LAMBDA_BI,
        l3=LAMBDA_TRI,
    ) -> float:
        """
        Linear interpolation smoothing.
        """

        # Unigram
        p1 = self.unigram[(w3,)] / self.total_tokens

        # Bigram
        p2 = 0
        if self.unigram[(w2,)] > 0:
            p2 = self.bigram[(w2, w3)] / self.unigram[(w2,)]

        # Trigram
        p3 = 0
        if self.bigram[(w1, w2)] > 0:
            p3 = self.trigram[(w1, w2, w3)] / self.bigram[(w1, w2)]

        return l3 * p3 + l2 * p2 + l1 * p1


# =============================================================================
# TEXT GENERATION ENGINE
# =============================================================================

class StoryGenerator:
    """
    Generates Urdu stories using trigram probabilities.
    """

    def __init__(self, model: TrigramLanguageModel, tokenizer: BPETokenizer):
        self.model = model
        self.tokenizer = tokenizer
        self.vocab_ids = list(tokenizer.id_to_token.keys())

    # -----------------------------------------------------------------

    def sample_next(self, w1: int, w2: int) -> int:
        """Sample next token probabilistically."""

        probs = [
            self.model.interpolated_probability(w1, w2, w3)
            for w3 in self.vocab_ids
        ]

        total = sum(probs)
        probs = [p / total for p in probs]

        return random.choices(self.vocab_ids, weights=probs)[0]

    # -----------------------------------------------------------------

    def generate(self, start_tokens: List[int]) -> str:
        """
        Generate story until <EOT>.
        """

        generated = start_tokens[:]

        while len(generated) < MAX_GENERATION_LENGTH:

            w1, w2 = generated[-2], generated[-1]
            next_token = self.sample_next(w1, w2)

            generated.append(next_token)

            if next_token == self.tokenizer.eot_id:
                break

        return "".join(
            self.tokenizer.id_to_token[t] for t in generated
        )


# =============================================================================
# MAIN PIPELINE
# =============================================================================

def main():

    random.seed(RANDOM_SEED)

    print("Loading tokenizer...")
    tokenizer = BPETokenizer(VOCAB_PATH, MERGES_PATH)

    print("Loading corpus...")
    texts = load_corpus(DATA_PATH)

    print("Tokenizing corpus...")
    tokenized = [tokenizer.encode(t) for t in texts]

    print("Training trigram model...")
    model = TrigramLanguageModel()
    model.train(tokenized)

    print("Generating sample story...")
    start = tokenizer.encode("<EOT>")
    generator = StoryGenerator(model, tokenizer)

    story = generator.generate(start)

    print("\n================ GENERATED STORY ================\n")
    print(story)


if __name__ == "__main__":
    main()
