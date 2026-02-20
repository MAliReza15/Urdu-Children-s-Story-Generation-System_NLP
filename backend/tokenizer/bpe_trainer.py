import json
from collections import defaultdict

SPECIAL_TOKENS = {"<EOT>", "<EOS>", "<EOP>"}

def get_unique_chars(texts):
    seen = {}
    for text in texts:
        tokens = tokenize_text(text)
        for tok in tokens:
            if tok not in seen:
                seen[tok] = None
    return list(seen.keys())

def tokenize_text(text):
    """Split text into characters, but keep special tokens as single units."""
    tokens = []
    i = 0
    while i < len(text):
        matched = False
        for st in SPECIAL_TOKENS:
            if text[i:i+len(st)] == st:
                tokens.append(st)
                i += len(st)
                matched = True
                break
        if not matched:
            tokens.append(text[i])
            i += 1
    return tokens

def get_pair_frequencies(all_token_ids, special_ids):
    pairs = defaultdict(int)
    for token_ids in all_token_ids:
        for i in range(len(token_ids) - 1):
            # Skip pairs that involve special tokens
            if token_ids[i] in special_ids or token_ids[i + 1] in special_ids:
                continue
            pairs[(token_ids[i], token_ids[i + 1])] += 1
    return pairs

def merge_pair(token_ids, pair, new_id):
    new_tokens = []
    i = 0
    while i < len(token_ids):
        if i < len(token_ids) - 1 and token_ids[i] == pair[0] and token_ids[i + 1] == pair[1]:
            new_tokens.append(new_id)
            i += 2
        else:
            new_tokens.append(token_ids[i])
            i += 1
    return new_tokens

def train_bpe(texts, vocab_size=250):
    # Step 1: Add all unique characters (and special tokens) to vocab
    unique_chars = get_unique_chars(texts)

    vocab = {}
    for idx, ch in enumerate(unique_chars):
        vocab[idx] = ch

    # Track special token IDs so they are never merged
    special_ids = {idx for idx, ch in vocab.items() if ch in SPECIAL_TOKENS}

    print(f"Initial vocab size (unique chars + special tokens): {len(vocab)}")
    print(f"Special token IDs: { {vocab[i]: i for i in special_ids} }")

    # Step 2: Initialize token_ids per text using tokenize_text
    char_to_id = {ch: idx for idx, ch in vocab.items()}
    all_token_ids = [[char_to_id[tok] for tok in tokenize_text(text)] for text in texts]

    merges = []
    next_id = len(vocab)

    # Step 3: Merge until vocab size reaches target
    while len(vocab) < vocab_size:
        pair_freqs = get_pair_frequencies(all_token_ids, special_ids)

        if not pair_freqs:
            print("No more pairs to merge.")
            break

        best_pair = max(pair_freqs, key=lambda p: pair_freqs[p])
        new_token = vocab[best_pair[0]] + vocab[best_pair[1]]

        vocab[next_id] = new_token
        merges.append([best_pair[0], best_pair[1], next_id, new_token])

        print(f"Merge #{len(merges):>3}: {repr(vocab[best_pair[0]])} + {repr(vocab[best_pair[1]])} "
              f"-> {repr(new_token)} (id={next_id}, freq={pair_freqs[best_pair]})")

        all_token_ids = [merge_pair(token_ids, best_pair, next_id) for token_ids in all_token_ids]
        next_id += 1

    return merges, vocab


# ── Main ───────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import argparse
    import os

    parser = argparse.ArgumentParser(description="Train BPE on preprocessed Urdu stories")
    parser.add_argument("--input", required=True, help="Path to processed stories JSON")
    parser.add_argument("--vocab-size", type=int, required=True, help="Target vocab size")
    parser.add_argument("--label", required=True, help="Story-set label (e.g. 500, 1000, all)")
    args = parser.parse_args()

    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    DATA_DIR = os.path.join(BASE_DIR, "Data")

    merges_path = os.path.join(DATA_DIR, f"merges_{args.label}_{args.vocab_size}.json")
    vocab_path = os.path.join(DATA_DIR, f"vocab_{args.label}_{args.vocab_size}.json")

    # Skip if both outputs already exist and are newer than or equal to input
    if os.path.exists(args.input):
        input_mtime = os.path.getmtime(args.input)
        if (os.path.exists(merges_path) and os.path.exists(vocab_path) and
                os.path.getmtime(merges_path) >= input_mtime and
                os.path.getmtime(vocab_path) >= input_mtime):
            print(f"\nSkipping (already trained): merges and vocab for {args.label} / vocab_size={args.vocab_size}")
            print(f"  Input: {args.input}")
            exit(0)

    print(f"\n{'='*60}")
    print(f"BPE Training: stories={args.label}  vocab_size={args.vocab_size}")
    print(f"Input: {args.input}")
    print(f"{'='*60}")

    with open(args.input, "r", encoding="utf-8") as f:
        data = json.load(f)

    texts = [story["content"] for story in data]
    print(f"Loaded {len(texts)} stories")

    merges, final_vocab = train_bpe(texts, vocab_size=args.vocab_size)

    with open(merges_path, "w", encoding="utf-8") as f:
        json.dump(merges, f, ensure_ascii=False, indent=2)

    with open(vocab_path, "w", encoding="utf-8") as f:
        json.dump({str(k): v for k, v in final_vocab.items()}, f, ensure_ascii=False, indent=2)

    print(f"\nDone. Vocab size: {len(final_vocab)} | Merges: {len(merges)}")
    print(f"Saved: {os.path.basename(merges_path)}, {os.path.basename(vocab_path)}")
