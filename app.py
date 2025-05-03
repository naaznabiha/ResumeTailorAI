from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter
from slowapi.util import get_remote_address
from scraper import scrape_linkedin_job
from openai import OpenAI
from dotenv import load_dotenv
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

# Initialize OpenAI client (NEW PROPER WAY FOR v1.0+)
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise RuntimeError("OPENAI_API_KEY not found in .env file")

client = OpenAI(
    api_key=api_key,
    # Remove any proxies parameter if you had it
)

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "ResumeTailorAI is LIVE!",
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

def tailor_resume(job_desc: str, resume: str) -> str:
    """Use OpenAI to tailor resume"""
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": "You are a professional career coach. Tailor this resume to match the job description."
                },
                {
                    "role": "user",
                    "content": f"Job Description:\n{job_desc}\n\nResume:\n{resume}"
                }
            ],
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"OpenAI error: {str(e)}"
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
        
        tailored_resume = tailor_resume(job_desc, resume_text)
        return {"tailored_resume": tailored_resume}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Resume tailoring failed: {str(e)}"
        )