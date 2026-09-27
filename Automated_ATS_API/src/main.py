from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Depends
from dotenv import load_dotenv
import os
import asyncio
import json
from sqlalchemy.orm import Session
from src.ai_engine import extract_text_from_pdf, parse_resume, calculate_match_score
from src.database import engine, Base, get_db, CandidateRecord

# Load environment variables from .env file so we don't hardcode secrets
load_dotenv()

# Initialize the FastAPI app
app = FastAPI(
    title="Smart ATS API",
    description="Automated Resume Parsing and Matching API using Gemini",
    version="1.0.0"
)

# Create database tables when the app starts
Base.metadata.create_all(bind=engine)

@app.get("/")
async def root():
    """
    Simple health check endpoint to make sure the server is breathing.
    Used async def so it doesn't block the event loop.
    """
    return {"status": "online", "message": "Smart ATS API is up and running!"}

@app.get("/health")
async def health_check(db: Session = Depends(get_db)):
    """
    More detailed health check. 
    Checks if API key is set and if database is reachable.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    key_status = "ok" if api_key and api_key != "your_api_key_here" else "warning"
    
    # Quick database ping
    db_status = "ok"
    try:
        db.execute("SELECT 1")
    except Exception:
        db_status = "error"
        
    return {
        "status": "healthy" if key_status == "ok" and db_status == "ok" else "warning", 
        "gemini_configured": key_status == "ok",
        "database_connected": db_status == "ok"
    }

@app.post("/evaluate-resume")
async def evaluate_resume(
    job_description: str = Form(..., description="The target Job Description text"),
    resume: UploadFile = File(..., description="The candidate's PDF resume"),
    db: Session = Depends(get_db)
):
    """
    Core ATS endpoint. 
    Takes a PDF and a JD, extracts text, parses to JSON, calculates match score, and logs to DB.
    """
    if not resume.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")
        
    try:
        # 1. Read PDF bytes
        file_bytes = await resume.read()
        
        # 2. Extract Text
        resume_text = extract_text_from_pdf(file_bytes)
        if len(resume_text) < 50:
            raise HTTPException(status_code=400, detail="Could not extract enough text from PDF. Might be an image.")
            
        # 3. Parse JSON & Calculate Score concurrently
        parsed_profile, match_score = await asyncio.gather(
            parse_resume(resume_text),
            calculate_match_score(resume_text, job_description)
        )
        
        # 4. Save to Database
        db_candidate = CandidateRecord(
            name=parsed_profile.name,
            email=parsed_profile.email,
            match_score=match_score,
            summary=parsed_profile.summary,
            skills=json.dumps(parsed_profile.skills)
        )
        db.add(db_candidate)
        db.commit()
        db.refresh(db_candidate) # Refresh to get the auto-generated ID
        
        return {
            "status": "success",
            "candidate_id": db_candidate.id,
            "match_score": match_score,
            "candidate_profile": parsed_profile.model_dump(),
        }
        
    except Exception as e:
        # Catching general exceptions so the server doesn't crash
        raise HTTPException(status_code=500, detail=str(e))

