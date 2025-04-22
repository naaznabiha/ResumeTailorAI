from bs4 import BeautifulSoup
import requests
import time

def scrape_linkedin_job(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Accept-Language": "en-US,en;q=0.9"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(response.text, 'html.parser')  # ← CHANGED TO html.parser
        return soup.get_text(separator='\n').strip()
    except Exception as e:
        print(f"⚠️ Scraping failed: {e}")
        return None
