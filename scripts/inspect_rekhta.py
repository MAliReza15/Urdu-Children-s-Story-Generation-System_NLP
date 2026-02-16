"""Inspect Rekhta.org DOM structure to determine correct CSS selectors."""
import requests
from bs4 import BeautifulSoup
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

# 1. Check a story page
print("=" * 60)
print("STORY PAGE: sabse-chhota-gham")
print("=" * 60)
r = requests.get('https://www.rekhta.org/stories/sabse-chhota-gham-abid-suhail-stories?lang=ur', headers=headers)
print(f"Status: {r.status_code}")
soup = BeautifulSoup(r.content, 'html.parser')

# Find title
h1 = soup.find('h1')
if h1:
    print(f"H1 class: {h1.get('class')}")
    print(f"H1 text: {h1.get_text(strip=True)[:100]}")
    # Check parent
    print(f"H1 parent tag: {h1.parent.name} class: {h1.parent.get('class')}")

# Find all divs with interesting classes
print("\n--- Divs with content-related classes ---")
for div in soup.find_all('div'):
    cls = div.get('class', [])
    cls_str = ' '.join(cls)
    if any(kw in cls_str.lower() for kw in ['poem', 'story', 'content', 'body', 'text']):
        text_preview = div.get_text(strip=True)[:80]
        print(f"DIV.{cls_str}: {text_preview}")

# Find paragraphs with Urdu content
print("\n--- Paragraphs with Urdu ---")
for p in soup.find_all('p')[:10]:
    text = p.get_text(strip=True)
    if len(text) > 20:
        print(f"P class={p.get('class')}: {text[:80]}")

# Check for any element containing the story text
print("\n--- Looking for story content container ---")
# Try various common selectors
for selector in ['div.poemPageContentBody', 'div.storyContent', 'div.contentBody', 
                 'div.poemBody', 'div#contentBody', 'div.mainContentBody',
                 '.contentListBody', '.poemPageContent', '.storyPageContentBody',
                 'div[class*=Content]', 'div[class*=content]']:
    elems = soup.select(selector)
    if elems:
        for e in elems[:2]:
            print(f"FOUND {selector}: class={e.get('class')} | text={e.get_text(strip=True)[:80]}")

# Dump all unique div classes
print("\n--- All unique div classes ---")
all_classes = set()
for div in soup.find_all('div'):
    cls = div.get('class', [])
    for c in cls:
        all_classes.add(c)
for c in sorted(all_classes):
    if any(kw in c.lower() for kw in ['poem', 'story', 'content', 'body', 'text', 'page', 'main']):
        print(f"  {c}")

# 2. Check author stories page
print("\n" + "=" * 60)
print("AUTHOR STORIES PAGE: abid-suhail")
print("=" * 60)
r2 = requests.get('https://www.rekhta.org/authors/abid-suhail/stories', headers=headers)
soup2 = BeautifulSoup(r2.content, 'html.parser')

story_links = []
for a in soup2.find_all('a', href=True):
    href = a['href']
    if '/stories/' in href and href.count('/') >= 2 and 'stories' != href.rstrip('/').split('/')[-1]:
        if href not in [s for s in story_links]:
            story_links.append(href)

print(f"Found {len(story_links)} story links:")
for link in story_links[:10]:
    print(f"  {link}")

# 3. Check main stories listing page
print("\n" + "=" * 60)
print("STORIES LISTING PAGE")
print("=" * 60)
r3 = requests.get('https://www.rekhta.org/stories', headers=headers)
soup3 = BeautifulSoup(r3.content, 'html.parser')

author_links = set()
for a in soup3.find_all('a', href=True):
    href = a['href']
    if ('/authors/' in href or '/storywriter/' in href) and '/stories' in href:
        author_links.add(href)

print(f"Found {len(author_links)} author/storywriter links")
for link in sorted(author_links)[:15]:
    print(f"  {link}")
