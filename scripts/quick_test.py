"""Quick test: verify each scraper can extract a story."""
import sys
import io
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.append(str(Path(__file__).parent.parent))

import yaml
with open('config/scraping_config.yaml', 'r', encoding='utf-8') as f:
    config = yaml.safe_load(f)

# ---- Test 1: Rekhta ----
print("=" * 60)
print("TEST 1: Rekhta - Extract a single story")
print("=" * 60)
try:
    from src.scraping.rekhta_scraper import RekhtaScraper
    scraper = RekhtaScraper(config)
    # Directly test extracting a known story
    story = scraper.extract_story("https://www.rekhta.org/stories/sabse-chhota-gham-abid-suhail-stories?lang=ur")
    if story:
        print(f"  SUCCESS! Title: {story['title'][:60]}")
        print(f"  Content length: {len(story['content'])} chars")
        print(f"  Content preview: {story['content'][:100]}...")
        print(f"  Author: {story.get('author', 'N/A')}")
    else:
        print("  FAILED: No story returned")
except Exception as e:
    print(f"  ERROR: {e}")

# ---- Test 2: BBC Urdu ----
print("\n" + "=" * 60)
print("TEST 2: BBC Urdu - Extract a single article")
print("=" * 60)
try:
    from src.scraping.bbc_scraper import BBCScraper
    scraper2 = BBCScraper(config)
    # Test extracting a known article
    story2 = scraper2.extract_story("https://www.bbc.com/urdu/articles/c0e5nd8j8wwo")
    if story2:
        print(f"  SUCCESS! Title: {story2['title'][:60]}")
        print(f"  Content length: {len(story2['content'])} chars")
        print(f"  Content preview: {story2['content'][:100]}...")
    else:
        print("  FAILED: No story returned")
except Exception as e:
    print(f"  ERROR: {e}")

# ---- Test 3: BBC Urdu - URL discovery ----
print("\n" + "=" * 60)
print("TEST 3: BBC Urdu - URL discovery from topic page")
print("=" * 60)
try:
    urls = scraper2.get_story_urls()
    print(f"  Found {len(urls)} article URLs")
    for u in urls[:5]:
        print(f"    {u}")
except Exception as e:
    print(f"  ERROR: {e}")

print("\n" + "=" * 60)
print("ALL TESTS COMPLETE")
print("=" * 60)
