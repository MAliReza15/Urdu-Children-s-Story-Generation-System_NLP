import time
import json
import sys
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
N = 2  # Number of stories
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

def getStoryLinks(minLinks):
    collectedLinks = set()
    pageNum = 1
    
    while len(collectedLinks) < minLinks:
        url = URL.format(pageNum)
        print(f'--- Scanning Page {pageNum}: {url} ---')
        
        try:
            driver.get(url)
            # Wait for content to load
            wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'title_en')))
            # Find all potential links
            elements = driver.find_elements(By.XPATH, "//p[contains(@class, 'title_en')]/ancestor::a")
            count = len(collectedLinks)
            for el in elements:
                if len(collectedLinks) >= minLinks:
                    break  
                href = el.get_attribute('href')
                if href and 'category' not in href:
                    if 'stories' in href and 'riddles' not in href and 'lateefay' not in href:
                        collectedLinks.add(href)
            
            found = len(collectedLinks) - count
            print(f'   Found {found} new STORY links. Total: {len(collectedLinks)}/{minLinks}')
            if found == 0:
                print('   No new valid stories found on this page. Stopping.')
                break

        except Exception as e:
            print(f'   Error on page {pageNum}: {e}')
            break
            
        pageNum += 1
        time.sleep(1)

    return list(collectedLinks)


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
        return ''
    parts = data.split(EOP)
    if len(parts) > 0:
        author = parts[0].strip()
        parts = parts[1:]
    else:
        author = ""
        parts = []
    reversed = parts[::-1]
    return EOT + EOP.join(reversed), author

# ---------------- MAIN ----------------
def main():
    try:
        links = getStoryLinks(N)
        print(f'\nCollection Complete. Scraping content for {len(links)} stories...\n')
        results = []
        for i, link in enumerate(links):
            print(f'[{i + 1}/{len(links)}] Scraping: {link}')
            data = getStory(link)
            if data and len(data['content']) > 20:
                data['content'], data['author'] = reverseParagraphs(data['content'])
                results.append(data)
                try:
                    title = data['title'].encode('ascii', 'ignore').decode('ascii')
                except:
                    title = 'Story'
                print(f'   Saved: {title}...')
            else:
                print('   Skipped (Empty or Error)')            
        with open('urduStories.json', 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        print(f'\nDone! Scraped {len(results)} stories.')

    finally:
        driver.quit()

if __name__ == '__main__':
    main()