#!/usr/bin/env python3
"""
ULTIMATE WORKING SCRAPER - JULY 2024
"""

import time
import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import json
from pathlib import Path
import os

# ======================
# 1. CONFIGURATION
# ======================
REQUEST_DELAY = 5
MAX_RETRIES = 3
DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)

# ======================
# 2. LINKEDIN SCRAPER
# ======================
def scrape_linkedin_job(url: str) -> str | None:
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
    }

    for attempt in range(MAX_RETRIES):
        try:
            time.sleep(REQUEST_DELAY)
            response = requests.get(url.strip(), headers=headers, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, "html.parser")
            job_desc = (soup.find("div", {"class": "jobs-description__content"}) or 
                       soup.find("div", {"class": "description__text"}))
            
            if job_desc:
                return "\n".join(line.strip() for line in job_desc.get_text().splitlines() if line.strip())
            return None

        except Exception as e:
            print(f"⚠️ Attempt {attempt + 1} failed: {str(e)}")
            if attempt == MAX_RETRIES - 1:
                return None

# ======================
# 3. DATA SAVER (FIXED VERSION)
# ======================
def save_job_description(job_data: dict) -> None:
    output_file = DATA_DIR / "job_descriptions.json"
    
    # Initialize empty list if file doesn't exist or is invalid
    if not output_file.exists() or os.stat(output_file).st_size == 0:
        existing_data = []
    else:
        try:
            with open(output_file, "r", encoding="utf-8") as f:
                existing_data = json.load(f)
        except json.JSONDecodeError:
            existing_data = []
    
    existing_data.append(job_data)
    
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(existing_data, f, indent=2)

# ======================
# 4. MAIN EXECUTION
# ======================
if __name__ == "__main__":
    test_url = "https://www.linkedin.com/jobs/view/3891664774"
    
    print("=== LINKEDIN TEST ===")
    if desc := scrape_linkedin_job(test_url):
        print("\n=== FIRST 300 CHARACTERS ===")
        print(desc[:300] + "...")
        
        save_job_description({
            "source": "linkedin",
            "url": test_url,
            "description": desc
        })
        print("\n✅ Saved to data/job_descriptions.json")
        
        # Verify the saved file
        with open(DATA_DIR / "job_descriptions.json", "r", encoding="utf-8") as f:
            print(f"\n📄 File content verification:")
            print(json.dumps(json.load(f), indent=2)[:200] + "...")
    else:
        print("\n❌ Failed to scrape job description")