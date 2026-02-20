import re
import unicodedata
import json
import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "Data")

def normalize_urdu(text):
    # Unicode normalization
    text = unicodedata.normalize('NFKC', text)

    # Remove diacritics
    text = re.sub(r'[\u064B-\u065F\u0670]', '', text)

    # Replace Arabic chars with Urdu standard
    replacements = {
        'ي': 'ی',
        'ى': 'ی',
        'ك': 'ک',
        'ه': 'ہ',
        'ة': 'ہ'
    }
    for src, tgt in replacements.items():
        text = text.replace(src, tgt)

    # Remove Tatweel
    text = text.replace('ـ', '')

    # Remove extra spaces
    text = re.sub(r'\s+', ' ', text).strip()

    return text

def replace_tags(text):
    text = text.replace("\\e", " <EOT> ")
    text = text.replace("\\p", " <EOP> ")
    return text


def add_eos(text):
    text = re.sub(r'([۔!?])', r'\1 <EOS> ', text)
    return text


def preprocess_story(text):
    text = replace_tags(text)
    text = normalize_urdu(text)
    text = add_eos(text)
    return text


def process_file(input_path, output_path):
    """Load, preprocess, and save a single JSON file."""
    print(f"Processing: {os.path.basename(input_path)} -> {os.path.basename(output_path)}")

    with open(input_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    for story in data:
        story["content"] = preprocess_story(story["content"])

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"  Saved {len(data)} stories to {output_path}")


if __name__ == "__main__":
    # Default: process all three files
    files_to_process = {
        "urduStories.json":      "processed_stories.json",
        "urduStories_500.json":  "processed_stories_500.json",
        "urduStories_1000.json": "processed_stories_1000.json",
    }

    for src_name, dst_name in files_to_process.items():
        src = os.path.join(DATA_DIR, src_name)
        dst = os.path.join(DATA_DIR, dst_name)

        if not os.path.exists(src):
            print(f"Skipping (not found): {src}")
            continue

        # Skip if output already exists and is newer than or equal to source
        if os.path.exists(dst):
            src_mtime = os.path.getmtime(src)
            dst_mtime = os.path.getmtime(dst)
            if dst_mtime >= src_mtime:
                print(f"Skipping (already processed): {src_name}")
                continue

        process_file(src, dst)

