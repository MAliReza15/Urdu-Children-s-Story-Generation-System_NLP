"""
Run BPE training for all combinations of story sets and vocab sizes.
Outputs go to Data/ as merges_{label}_{vocab}.json and vocab_{label}_{vocab}.json
"""

import subprocess
import sys
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "Data")
TRAINER  = os.path.join(BASE_DIR, "tokenizer", "bpe_trainer.py")

# (input filename, label)
STORY_SETS = [
    ("processed_stories.json",      "all"),
]

VOCAB_SIZES = [250, 1000, 5000]


def main():
    total = len(STORY_SETS) * len(VOCAB_SIZES)
    run = 0

    for input_file, label in STORY_SETS:
        input_path = os.path.join(DATA_DIR, input_file)
        if not os.path.exists(input_path):
            print(f"SKIP (not found): {input_path}")
            continue

        for vs in VOCAB_SIZES:
            run += 1
            print(f"\n{'#'*60}")
            print(f"# Run {run}/{total}: stories={label}  vocab_size={vs}")
            print(f"{'#'*60}")

            cmd = [
                sys.executable, TRAINER,
                "--input", input_path,
                "--vocab-size", str(vs),
                "--label", label,
            ]
            result = subprocess.run(cmd)

            if result.returncode != 0:
                print(f"ERROR: run {run} failed with code {result.returncode}")

    print(f"\n{'='*60}")
    print(f"All {total} runs complete.")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
