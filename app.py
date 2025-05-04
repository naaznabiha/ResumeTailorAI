from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter
from slowapi.util import get_remote_address
from scraper import scrape_linkedin_job
from dotenv import load_dotenv  # Added this import
import httpx
import os

# Load environment variables first
load_dotenv()  # Now this will work

# Initialize FastAPI
app = FastAPI(
    title="ResumeTailorAI",
    docs_url="/docs",
    redoc_url=None
)

# Rate limiting
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST"],
    allow_headers=["*"]
)

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "ResumeTailorAI is LIVE! (Now with Local LLM)",
        "endpoints": {
            "scrape": "/scrape?url=LINKEDIN_JOB_URL",
            "tailor": "POST /tailor"
        }
    }

@app.get("/scrape")
@limiter.limit("5/minute")
async def scrape_job(request: Request, url: str):
    """
    Scrape LinkedIn job description
    """
    if not url.startswith(("https://www.linkedin.com", "https://linkedin.com")):
        raise HTTPException(
            status_code=400,
            detail="Only LinkedIn URLs are supported"
        )
    
    try:
        description = scrape_linkedin_job(url)
        if not description:
            raise HTTPException(
                status_code=404,
                detail="Job description not found"
            )
        return {"description": description}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Scraping failed: {str(e)}"
        )

async def tailor_resume(job_desc: str, resume: str) -> str:
    """Use local Llama3 to tailor resume"""
    try:
        prompt = f"""
        [INST] <<SYS>>
        You are an expert career coach. Strictly follow these rules:
        1. Keep original resume structure
        2. Highlight skills matching: {job_desc[:1000]}
        3. Never add fake information
        4. Respond ONLY with optimized resume text
        <</SYS>>
        
        Optimize this resume:
        {resume}
        [/INST]
        """
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": "llama3",
                    "prompt": prompt,
                    "stream": False,
                    "options": {"temperature": 0.7}
                },
                timeout=60.0  # Increased timeout for local LLM
            )
            return response.json()["response"]
            
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"AI processing error: {str(e)}"
        )

@app.post("/tailor")
@limiter.limit("3/minute")
async def tailor_resume_api(request: Request, job_url: str, resume_text: str):
    """
    Tailor resume to a job posting
    """
    try:
        job_desc = scrape_linkedin_job(job_url)
        if not job_desc:
            raise HTTPException(
                status_code=400,
                detail="Could not scrape job description"
            )
        
        tailored_resume = await tailor_resume(job_desc, resume_text)
        return {"tailored_resume": tailored_resume}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Resume tailoring failed: {str(e)}"
        )