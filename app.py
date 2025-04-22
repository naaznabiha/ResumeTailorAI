from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from scraper import scrape_linkedin_job
from pathlib import Path

app = FastAPI(title="ResumeTailorAI", docs_url="/docs")

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "ResumeTailorAI is LIVE!",
        "endpoints": {
            "scrape": "/scrape?url=LINKEDIN_JOB_URL"
        }
    }

@app.get("/scrape")
async def scrape_job(url: str):
    """
    Scrape LinkedIn job description
    
    Parameters:
    - url: Valid LinkedIn job URL
    
    Returns:
    - JSON with 'description' field or error message
    
    Status codes:
    - 200: Success
    - 400: Invalid URL format
    - 500: Scraping failed
    """
    if not url.startswith(("https://www.linkedin.com", "https://linkedin.com")):
        raise HTTPException(
            status_code=400,
            detail="Only LinkedIn URLs are supported. Example: https://www.linkedin.com/jobs/view/123456789"
        )
    
    try:
        if description := scrape_linkedin_job(url):
            return {"description": description}
        raise HTTPException(
            status_code=500,
            detail="Scraping failed - LinkedIn may have blocked the request"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )