from fastapi import FastAPI
from dotenv import load_dotenv

load_dotenv()  # Load .env file
app = FastAPI()  # <- Must be lowercase "app"

@app.get("/")
def home():
    return {"message": "ResumeTailorAI is running!"}