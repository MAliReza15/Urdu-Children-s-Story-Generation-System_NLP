"""Inspect BBC Urdu DOM structure to determine correct CSS selectors."""
import requests
from bs4 import BeautifulSoup
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

# 1. Check topic listing page
print("=" * 60)
print("BBC URDU TOPIC PAGE: Pakistan")
print("=" * 60)
r = requests.get('https://www.bbc.com/urdu/topics/cjgn7n9zzq7t', headers=headers)
print(f"Status: {r.status_code}")
soup = BeautifulSoup(r.content, 'html.parser')

# Find article links
article_links = set()
for a in soup.find_all('a', href=True):
    href = a['href']
    if '/urdu/articles/' in href:
        if href.startswith('/'):
            href = 'https://www.bbc.com' + href
        article_links.add(href)

print(f"Found {len(article_links)} article links")
for link in sorted(article_links)[:10]:
    print(f"  {link}")

# Check what selectors work for the listing
print("\n--- Article list containers ---")
for elem in soup.find_all(['article', 'div'], attrs={'data-testid': True})[:10]:
    testid = elem.get('data-testid')
    print(f"  {elem.name}[data-testid={testid}]")

# 2. Check an article page
print("\n" + "=" * 60)
print("BBC URDU ARTICLE PAGE")
print("=" * 60)

# Get first article link
if article_links:
    article_url = sorted(article_links)[0]
    print(f"Checking: {article_url}")
    r2 = requests.get(article_url, headers=headers)
    print(f"Status: {r2.status_code}")
    soup2 = BeautifulSoup(r2.content, 'html.parser')

    # Title
    h1 = soup2.find('h1')
    if h1:
        print(f"H1 id={h1.get('id')} class={h1.get('class')}: {h1.get_text(strip=True)[:100]}")

    # Content - check various selectors
    for selector in ['div.article-body p', 'article p', 'div[data-component="text-block"]',
                     'div.ssrcss-11r1m41-RichTextComponentWrapper p', 'main p',
                     'div.bbc-19j92fr p', 'p[dir="rtl"]']:
        elems = soup2.select(selector)
        if elems:
            print(f"\nSELECTOR '{selector}' found {len(elems)} elements:")
            for e in elems[:3]:
                print(f"  {e.get_text(strip=True)[:80]}")

    # Check main article structure
    print("\n--- Main/Article structure ---")
    main = soup2.find('main')
    if main:
        for p in main.find_all('p')[:5]:
            cls = p.get('class', [])
            print(f"  P class={cls} dir={p.get('dir')}: {p.get_text(strip=True)[:80]}")

    # data-component blocks
    print("\n--- data-component blocks ---")
    for div in soup2.find_all(attrs={'data-component': True})[:10]:
        comp = div.get('data-component')
        print(f"  {div.name}[data-component={comp}]")
