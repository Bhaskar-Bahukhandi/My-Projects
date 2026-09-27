import math
import io
import asyncio
from pypdf import PdfReader
from pydantic import BaseModel, Field
from google import genai
from google.genai import types
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from google.genai.errors import APIError

# Define the exact JSON structure we want the LLM to output
class CandidateProfile(BaseModel):
    name: str = Field(description="Full name of the candidate")
    email: str = Field(description="Email address of the candidate")
    skills: list[str] = Field(description="List of technical and soft skills extracted")
    years_of_experience: int = Field(description="Estimated total years of professional experience")
    summary: str = Field(description="A brief 2-sentence summary of the candidate's profile")

def extract_text_from_pdf(file_bytes: bytes) -> str:
    """
    Extracts raw text from a PDF file.
    """
    try:
        reader = PdfReader(io.BytesIO(file_bytes))
        text = ""
        for page in reader.pages:
            extracted = page.extract_text()
            if extracted:
                text += extracted + "\n"
        return text.strip()
    except Exception as e:
        print(f"Error reading PDF: {e}")
        return ""

# Robust retry logic from our previous RAG project architecture
@retry(
    stop=stop_after_attempt(4), 
    wait=wait_exponential(multiplier=1, min=2, max=15),
    reraise=True
)
async def parse_resume(resume_text: str) -> CandidateProfile:
    """
    Uses Gemini Structured Outputs to turn messy resume text into clean JSON.
    Wrapped in exponential backoff to survive 503/429 outages.
    """
    client = genai.Client() 
    prompt = f"Please extract the following candidate details from this resume text:\n\n{resume_text}"
    
    interaction = await client.aio.interactions.create(
        model='gemini-3.7-flash',
        input=prompt,
        generation_config={"temperature": 0.1},
        response_format={
            "type": "text",
            "mime_type": "application/json",
            "schema": CandidateProfile.model_json_schema()
        }
    )
    return CandidateProfile.model_validate_json(interaction.output_text)

@retry(
    stop=stop_after_attempt(4), 
    wait=wait_exponential(multiplier=1, min=2, max=15),
    reraise=True
)
async def get_embedding(client, text: str):
    """Helper with built-in retry for embeddings"""
    res = await client.aio.models.embed_content(
        model='gemini-embedding-2',
        contents=text
    )
    return res.embeddings[0].values

async def calculate_match_score(resume_text: str, jd_text: str) -> float:
    """
    Generates vector embeddings and calculates Cosine Similarity manually.
    """
    client = genai.Client()
    
    # Await both embedding generations concurrently
    resume_emb, jd_emb = await asyncio.gather(
        get_embedding(client, resume_text),
        get_embedding(client, jd_text)
    )
    
    # Calculate Cosine Similarity
    dot_product = sum(a * b for a, b in zip(resume_emb, jd_emb))
    norm_a = math.sqrt(sum(a * a for a in resume_emb))
    norm_b = math.sqrt(sum(b * b for b in jd_emb))
    
    if norm_a == 0 or norm_b == 0:
        return 0.0
        
    similarity = dot_product / (norm_a * norm_b)
    return round(similarity * 100, 2)
