from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware  # For frontend connections
from scraper import scrape_linkedin_job
from pathlib import Path
import uvicorn  # Required for Railway/Vercel

app = FastAPI()

# Allow all origins (replace * with your frontend URL later)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def home():
    return {"message": "ResumeTailorAI is LIVE!"}

@app.get("/scrape")
async def scrape_job(url: str):
    """Scrape a job description"""
    if not url.startswith(("https://www.linkedin.com", "https://linkedin.com")):
        raise HTTPException(status_code=400, detail="Only LinkedIn URLs are supported")
    
    if description := scrape_linkedin_job(url):
        return {"description": description}
    raise HTTPException(status_code=500, detail="Scraping failed")

# Required for Railway/Vercel
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)