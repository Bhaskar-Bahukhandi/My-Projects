import sys
import os
import asyncio
import logging
from typing import Dict, Any

# Needed this so I can run the script directly from the terminal without PYTHONPATH headaches
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from google import genai
from google.genai.errors import APIError
from config.settings import config

# Keeping logging simple for local dev
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

class GeminiClient:
    # Wrapping the SDK because Google's rate limits (429s) on the free tier 
    # were crashing my PDF ingestion script halfway through the textbooks.
    
    def __init__(self, max_retries: int = 3, backoff_factor: float = 2.0):
        self.client = genai.Client(api_key=config.gemini_api_key)
        self.chat_model = config.chat_model
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor

    async def generate_text(self, prompt: str) -> Dict[str, Any]:
        delay = 1.0
        
        for attempt in range(self.max_retries + 1):
            try:
                # Offloading to executor since the underlying generate_content blocks the event loop.
                # TODO(bhaskar): Migrate to genai's native async methods once they are stable in the SDK.
                loop = asyncio.get_running_loop()
                response = await loop.run_in_executor(
                    None,
                    lambda: self.client.models.generate_content(
                        model=self.chat_model,
                        contents=prompt
                    )
                )
                
                text = response.text or ""
                tokens = 0
                if hasattr(response, 'usage_metadata') and response.usage_metadata:
                    tokens = response.usage_metadata.total_token_count
                
                # print(f"DEBUG: used {tokens} tokens")
                return {"text": text, "tokens": tokens}
                
            except APIError as e:
                # specifically catching 429s and 503s to prevent the RAG pipeline from dying
                if "429" in str(e) or "Quota" in str(e) or "503" in str(e) or "UNAVAILABLE" in str(e):
                    if attempt == self.max_retries:
                        logger.error("Hit max retries on Gemini API. Crashing.")
                        raise
                    
                    # logger.info(f"Rate limited or server unavailable. Sleeping for {delay}s...")
                    await asyncio.sleep(delay)
                    delay *= self.backoff_factor
                else:
                    raise
                    
        return {"text": "", "tokens": 0}

    async def generate_embeddings_batch(self, texts: list[str]) -> list[list[float]]:
        """
        Generates embeddings for a batch of strings. 
        """
        if not texts:
            return []
            
        delay = 1.0
        for attempt in range(self.max_retries + 1):
            try:
                # In the new google-genai SDK, passing a list of strings to contents 
                # merges them into a single Content object, returning 1 embedding instead of N.
                # To get N embeddings, we fetch them concurrently using the native async client.
                tasks = [
                    self.client.aio.models.embed_content(
                        model=config.embed_model,
                        contents=t
                    )
                    for t in texts
                ]
                responses = await asyncio.gather(*tasks)
                
                # Extract the raw float arrays from each response
                return [res.embeddings[0].values for res in responses]
                
            except APIError as e:
                if "429" in str(e) or "Quota" in str(e) or "503" in str(e) or "UNAVAILABLE" in str(e):
                    if attempt == self.max_retries:
                        logger.error("Hit max retries on embeddings API.")
                        raise
                    
                    logger.warning(f"Embeddings rate limited or unavailable. Sleeping {delay}s...")
                    await asyncio.sleep(delay)
                    delay *= self.backoff_factor
                else:
                    raise
        
        return []

async def _test_connection():
    client = GeminiClient()
    print("Testing API connection...")
    
    try:
        result = await client.generate_text("Explain the concept of RAG in one sentence.")
        print(result["text"])
    except Exception as e:
        print(f"Failed: {e}")

if __name__ == "__main__":
    asyncio.run(_test_connection())
