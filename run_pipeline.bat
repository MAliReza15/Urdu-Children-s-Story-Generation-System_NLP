@echo off
echo Running Scraper (Rekhta) using venv...
venv\Scripts\python.exe scripts/run_scraper.py --source rekhta

echo Running Scraper (BBC Urdu) using venv...
venv\Scripts\python.exe scripts/run_scraper.py --source bbc_urdu

echo Running Scraper (UrduPoint) using venv...
venv\Scripts\python.exe scripts/run_scraper.py --source urdupoint

echo Running Preprocessing...
venv\Scripts\python.exe scripts/run_preprocessing.py --input data/raw --output data/processed

echo Generating Statistics...
venv\Scripts\python.exe scripts/generate_statistics.py --corpus data/processed/stories.json

echo Done! Output is in data/processed/stories.json and data/metadata/statistics.json.
