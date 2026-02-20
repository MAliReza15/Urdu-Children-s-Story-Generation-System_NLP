import time
import json
import sys
import random
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# Force UTF-8
sys.stdout.reconfigure(encoding='utf-8')

# Base link
URL = "https://www.urdupoint.com/kids/section/stories-page{}.html"
TARGET_NEW_STORIES = 500  # Number of NEW stories to find
BATCH_SIZE = 10     # Process stories in batches of this size
OUTPUT_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'urduStories.json')

EOP = r'\p' # EOP Tag for now
EOT = r'\e' # EOT Tag for now

# ---------------- DRIVER SETUP ----------------
chrome_options = Options()
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--start-maximized")
prefs = {"profile.managed_default_content_settings.images": 2}
chrome_options.add_experimental_option("prefs", prefs)

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)
wait = WebDriverWait(driver, 10)

# ---------------- FUNCTIONS ----------------

def load_existing_data(filepath):
    """Loads existing stories and returns them as a list and a set of URLs."""
    if not os.path.exists(filepath):
        return [], set()
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
            urls = {item['url'] for item in data if 'url' in item}
            return data, urls
    except Exception as e:
        print(f"Error loading existing data: {e}")
        return [], set()

def getStoryLinks(target_new, existing_urls):
    collected_new_links = set()
    pageNum = 1
    
    print(f"Scanning for {target_new} NEW stories (skipping {len(existing_urls)} existing)...")

    while len(collected_new_links) < target_new:
        url = URL.format(pageNum)
        print(f'--- Scanning Page {pageNum}: {url} ---')
        
        try:
            driver.get(url)
            # Wait for content to load
            wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'title_en')))
            
            # Find all potential links
            elements = driver.find_elements(By.XPATH, "//p[contains(@class, 'title_en')]/ancestor::a")
            
            initial_count = len(collected_new_links)
            
            for el in elements:
                if len(collected_new_links) >= target_new:
                    break
                
                href = el.get_attribute('href')
                if href and 'category' not in href:
                    if 'stories' in href and 'riddles' not in href and 'lateefay' not in href:
                        if href not in existing_urls and href not in collected_new_links:
                            collected_new_links.add(href)
            
            found_on_page = len(collected_new_links) - initial_count
            print(f'   Found {found_on_page} NEW links. Total New: {len(collected_new_links)}/{target_new}')
            
            if found_on_page == 0 and len(elements) == 0:
                 print('   No stories found on this page via XPath. Stopping scan.')
                 break
            if found_on_page == 0:
                print('   (Only duplicates or invalid links found on this page)')

        except Exception as e:
            print(f'   Error on page {pageNum}: {e}')
            break
            
        pageNum += 1
        time.sleep(random.uniform(1, 2)) # Polite delay between pages

    return list(collected_new_links)


def getStory(url):
    driver.get(url)

    try:
        wait.until(EC.presence_of_element_located((By.TAG_NAME, 'h1')))
        title = driver.find_element(By.TAG_NAME, 'h1').text.strip()

        try:
            # 1. Target the main story container
            content = wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'txt_detail')))
            # 2. Extract ALL text
            text = content.text
            # 3. Split into lines
            lines = text.split('\n')
            # 4. Clean formatting
            cleanLines = []
            for line in lines:
                cleaned = line.strip()
                if len(cleaned) > 0:
                     cleanLines.append(cleaned)
            # 5. Join with EOS
            content = EOP.join(cleanLines)
        except Exception as e:
            print(f'   (Extraction Error: {e})')
            content = ''

        return {'url': url, 'title': title, 'content': content}

    except Exception as e:
        print(f'   Failed to scrape {url}: {e}')
        return None
    
def reverseParagraphs(data):
    if not data:
        return '', ''
    parts = data.split(EOP)
    if len(parts) > 0:
        author = parts[0].strip()
        parts = parts[1:]
    else:
        author = ""
        parts = []
    reversed_parts = parts[::-1]
    return EOT + EOP.join(reversed_parts), author

def save_data(data, filepath):
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"   Saved {len(data)} total stories to {filepath}")

# ---------------- MAIN ----------------
def main():
    try:
        # 1. Load existing data
        all_stories, existing_ids = load_existing_data(OUTPUT_FILE)
        
        # 2. Find NEW links
        new_links = getStoryLinks(TARGET_NEW_STORIES, existing_ids)
        
        if not new_links:
            print("No new links found.")
            return

        print(f'\nCollection Complete. Starting Batch Scraping for {len(new_links)} new stories...\n')
        
        # 3. Batch Process
        total_batches = (len(new_links) + BATCH_SIZE - 1) // BATCH_SIZE
        
        for batch_num in range(total_batches):
            start_idx = batch_num * BATCH_SIZE
            end_idx = min(start_idx + BATCH_SIZE, len(new_links))
            batch_links = new_links[start_idx:end_idx]
            
            print(f'--- Processing Batch {batch_num + 1}/{total_batches} ({len(batch_links)} stories) ---')
            
            for i, link in enumerate(batch_links):
                global_idx = start_idx + i + 1
                print(f'[{global_idx}/{len(new_links)}] Scraping: {link}')
                
                data = getStory(link)
                
                if data and len(data['content']) > 20:
                    data['content'], data['author'] = reverseParagraphs(data['content'])
                    all_stories.append(data) # Add to main list
                    
                    try:
                        title_safe = data['title'].encode('ascii', 'ignore').decode('ascii')
                    except:
                        title_safe = 'Story'
                    print(f'   Scraped: {title_safe}...')
                else:
                    print('   Skipped (Empty or Error)')
                
                # Polite delay between items in a batch
                s_time = random.uniform(2, 5)
                time.sleep(s_time)

            # Save progress after each batch
            save_data(all_stories, OUTPUT_FILE)
            
            if batch_num < total_batches - 1:
                sleep_time = random.uniform(30, 60)
                print(f'   Batch complete. Sleeping for {sleep_time:.1f} seconds to avoid detection...')
                time.sleep(sleep_time)
        
        print(f'\nDone! Scraped {len(all_stories)} total stories.')

    finally:
        driver.quit()

if __name__ == '__main__':
    main()