from fastapi import FastAPI
from dotenv import load_dotenv
from scraper import scrape_linkedin_job

# Initialize app FIRST
load_dotenv()
app = FastAPI()  # This must come BEFORE any @app decorators

@app.get("/")
def home():
    return {"message": "ResumeTailorAI is running!"}

@app.get("/scrape")
async def scrape_job(url: str):
    """Scrape a job description"""
    if not url.startswith(("https://www.linkedin.com", "https://linkedin.com")):
        return {"error": "Only LinkedIn URLs are supported"}
    
    description = scrape_linkedin_job(url)
    return {"description": description} if description else {"error": "Scraping failed"}