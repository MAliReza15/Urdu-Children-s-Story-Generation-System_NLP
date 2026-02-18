import random
import sys

sys.stdout.reconfigure(encoding='utf-8')

from config import *
from data.data_loader import load_corpus
from tokenizer.bpe_tokenizer import BPETokenizer
from models.trigram_llm import TrigramLanguageModel
from generation.generator import StoryGenerator


def main():

    random.seed(RANDOM_SEED)

    tokenizer = BPETokenizer(VOCAB_PATH, MERGES_PATH)

    texts = load_corpus(DATA_PATH)
    tokenized = [tokenizer.encode(t) for t in texts]

    model = TrigramLanguageModel()
    model.train(tokenized)

    generator = StoryGenerator(model, tokenizer)

    start = [tokenizer.eot_id, tokenizer.eot_id]
    story = generator.generate(start)

    print("\n===== GENERATED STORY =====\n")
    print(story)


if __name__ == "__main__":
    main()
