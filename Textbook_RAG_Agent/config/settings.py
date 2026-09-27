import os
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# Load env variables before constructing settings so it doesn't crash on import
load_dotenv()

class AgentSettings(BaseModel):
    """
    Core configuration for the Textbook RAG Agent.
    Using Pydantic here so we get automatic type validation instead of fighting with os.getenv strings.
    """
    
    gemini_api_key: str = Field(default_factory=lambda: os.getenv("GEMINI_API_KEY", ""))
    
    # Models
    embed_model: str = "gemini-embedding-2"
    chat_model: str = "gemini-3.5-flash-lite"
    
    # RAG Tuning Parameters
    # TODO(bhaskar): 1024 chunks might be too big for dense textbook pages. Try dropping to 512 later if retrieval accuracy is bad.
    chunk_size: int = 1024
    chunk_overlap: int = 128

config = AgentSettings()

if not config.gemini_api_key:
    # Fail fast so we don't start the UI without a valid key
    raise ValueError("GEMINI_API_KEY environment variable is missing. Did you forget to set up the .env file?")
