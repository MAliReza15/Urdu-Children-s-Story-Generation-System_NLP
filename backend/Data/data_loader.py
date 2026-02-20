import json
from typing import List


def load_corpus(path: str) -> List[str]:
    """
    Load processed stories from JSON file.
    """
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    return [story["content"] for story in data]
