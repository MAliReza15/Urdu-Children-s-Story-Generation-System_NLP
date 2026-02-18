import re
import unicodedata
import json
import os

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


with open(r"c:\NLP\Urdu-Children-s-Story-Generation-System_NLP\Scraping\urduStories.json", "r", encoding="utf-8") as f:
    data = json.load(f)

for story in data:
    story["content"] = preprocess_story(story["content"])


output_file = r"c:\NLP\Urdu-Children-s-Story-Generation-System_NLP\Data\processed_stories.json"
os.makedirs(os.path.dirname(output_file), exist_ok=True)

with open(output_file, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

