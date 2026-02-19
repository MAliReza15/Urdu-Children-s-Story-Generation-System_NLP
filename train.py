import random
import sys
import argparse

sys.stdout.reconfigure(encoding='utf-8')

from config import *
from data.data_loader import load_corpus
from tokenizer.bpe_tokenizer import BPETokenizer
from models.model_factory import get_model
from generation.generator import StoryGenerator


# -------------------------------------------------------------

def parse_args():
    """
    Allows model selection from command line.
    Example:
        python train.py --model trigram
        python train.py --model 5gram
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--model",
        type=str,
        default="trigram",
        help="Language model type (trigram, 5gram, ...)"
    )
    return parser.parse_args()


# -------------------------------------------------------------

def main():

    args = parse_args()

    random.seed(RANDOM_SEED)

    print(f"\nLoading tokenizer...")
    tokenizer = BPETokenizer(VOCAB_PATH, MERGES_PATH)

    print("Loading corpus...")
    texts = load_corpus(DATA_PATH)

    print("Tokenizing corpus...")
    tokenized = [tokenizer.encode(t) for t in texts]

    print(f"Initializing {args.model} model...")
    model = get_model(args.model)

    print("Training model...")
    model.train(tokenized)

    print("Generating story...")
    generator = StoryGenerator(model, tokenizer)

    # Dynamic start tokens based on N-gram size
    start = [tokenizer.eot_id] * (model.n - 1)

    story = generator.generate(start)

    print("\n===== GENERATED STORY =====\n")
    print(story)


# -------------------------------------------------------------

if __name__ == "__main__":
    main()
