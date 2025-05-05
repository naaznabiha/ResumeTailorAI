from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter
from slowapi.util import get_remote_address
from scraper import scrape_linkedin_job
from dotenv import load_dotenv
import httpx
import os

# Load environment variables first
load_dotenv()

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
        You are a professional resume optimization expert. Follow these rules STRICTLY:
        1. PRESERVE FORMAT: Maintain original sections (Experience, Education, etc.)
        2. RELEVANCE FIRST: Bold **only** skills/experiences matching: {job_desc[:800]}
        3. NEVER INVENT: Only use information from the original resume
        4. OUTPUT FORMAT: Return clean markdown with ### Headers and - Bullet points
        5. LENGTH: Keep similar length to original (add/remove nothing)
        
        JOB DESCRIPTION KEYWORDS TO MATCH:
        {', '.join(set(job_desc.lower().split()[:20]))}
        <</SYS>>
        
        ORIGINAL RESUME TO OPTIMIZE:
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
                    "options": {
                        "temperature": 0.5,  # More focused outputs
                        "repeat_penalty": 1.1  # Prevents word repetition
                    }
                },
                timeout=60.0
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