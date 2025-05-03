import requests
from bs4 import BeautifulSoup
import time
import random
import re
# Updated June 2024 headers
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.google.com/",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"
}

def extract_salary(text):
    match = re.search(r"Salary\s*:\s*(.+)", text)
    return match.group(1) if match else None

def clean_text(text):
    return "\n".join(line.strip() for line in text.split("\n") 
            if line.strip() and "Show" not in line)

def scrape_linkedin_job(url):
    """Simplified but working version"""
    try:
        # Human-like delay
        time.sleep(random.uniform(2, 4))
        
        response = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # June 2024 working selectors
        job_desc = (
            soup.find('div', {'class': 'jobs-description__content'}) or
            soup.find('div', {'class': 'description__text'}) or
            soup.find('section', {'class': 'core-section-container'})
        )
        
        if job_desc:
            return " ".join(job_desc.get_text().strip().split())
        return None
        
    except Exception as e:
        print(f"⚠️ Error: {e}")