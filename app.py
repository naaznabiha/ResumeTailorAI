from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from scraper import scrape_linkedin_job
from pathlib import Path
import uvicorn

app = FastAPI()

# CORS (Keep this exactly as is)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 1. Changed root endpoint from home() to root() for convention
@app.get("/")
async def root():  # ← Renamed from home()
    return {"message": "ResumeTailorAI is LIVE!"}

# 2. Added status code to scrape_job docs
@app.get("/scrape")
async def scrape_job(url: str):
    """Scrape a job description
    Status codes:
      - 200: Success
      - 400: Invalid URL
      - 500: Scraping failed
    """
    if not url.startswith(("https://www.linkedin.com", "https://linkedin.com")):
        raise HTTPException(status_code=400, detail="Only LinkedIn URLs are supported")
    
    if description := scrape_linkedin_job(url):
        return {"description": description}
    raise HTTPException(status_code=500, detail="Scraping failed")

# 3. REMOVED the __main__ block (Railway uses Procfile)
# (This prevents double instantiation)