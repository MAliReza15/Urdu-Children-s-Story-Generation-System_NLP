Urdu Story Generation AI
🎯 Phase I: Data Collection & Preprocessing

This script automates the scraping and structuring of Urdu stories from UrduPoint to build a training corpus for a custom language model.
🚀 Core Functionalities

    Selenium Scraper: Extracts story links and content across multiple pages.

    Text Cleaning: Removes HTML noise and identifies main story text.

    Special Tokens: Implements placeholders for structural markers:

        <EOP> (End of Paragraph): Represented as \p.

        <EOT> (End of Story): Represented as \e.

    JSON Output: Saves data with UTF-8 encoding for Urdu script preservation.

🛠️ Technical Stack

    Python 3.x

    Selenium & WebDriver Manager

    JSON (Data Storage)

📥 Setup & Usage

    Install: pip install selenium webdriver-manager

    Configure: Set N = 200 in the script to meet the dataset requirement.

    Run: python scraper.py

📅 Project Roadmap

    ✅ Phase I: Dataset Collection (Current)

    ➡️ Phase II: Train Custom BPE Tokenizer (Vocab Size: 250)

    ➡️ Phase III: Tri-gram Probabilistic Model

    ➡️ Phase IV: Containerized Microservice

    ➡️ Phase V: Vercel UI Deployment