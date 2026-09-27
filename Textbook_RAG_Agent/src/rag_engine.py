import os
import sys
import logging
import asyncio
from typing import List, Dict

# Local imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import chromadb
from src.llm_client import GeminiClient
from config.settings import config

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

class TextbookRAGEngine:
    """
    The core 'Brain' of the application. 
    Wires together the Vector Database, the LLM, and the Context Memory.
    """
    
    def __init__(self, collection_name: str = "textbook_knowledge", top_k: int = 3):
        self.llm = GeminiClient()
        self.top_k = top_k
        
        db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "vector_store")
        self.chroma_client = chromadb.PersistentClient(path=db_path, settings=chromadb.Settings(anonymized_telemetry=False))
        
        # Using get_or_create instead of get, otherwise the app crashes on startup if the DB is empty.
        self.collection = self.chroma_client.get_or_create_collection(name=collection_name)
        
        # TODO(bhaskar): This memory list will grow infinitely if a user chats for hours.
        # Next month, we need to implement a sliding window (e.g., keep only the last 10 messages) 
        # so we don't blow up the Gemini context window and API bill.
        self.chat_history: List[Dict[str, str]] = []

    async def retrieve_context(self, query: str) -> str:
        """
        Embeds the user's question and performs a similarity search in ChromaDB.
        """
        # We manually embed using Gemini because we bypassed Chroma's default embedders in Month 9
        query_embs = await self.llm.generate_embeddings_batch([query])
        if not query_embs:
            return ""
            
        results = self.collection.query(
            query_embeddings=query_embs,
            n_results=self.top_k
        )
        
        # Extract the actual text chunks from the nested Chroma response
        if not results['documents'] or not results['documents'][0]:
            return ""
            
        retrieved_chunks = results['documents'][0]
        
        # Join the top chunks into a single context string
        # Added lines between chunks so the LLM knows they might be from different pages
        return "\n\n---\n\n".join(retrieved_chunks)

    def build_rag_prompt(self, query: str, context: str) -> str:
        """
        The Synthesizer Prompt. 
        This is what physically prevents the AI from hallucinating out-of-bounds knowledge.
        """
        # ---------------------------------------------------------
        # PROMPT ENGINEERING UPGRADE (Authentic Developer Note)
        # ---------------------------------------------------------
        # TODO(bhaskar): The original strict RAG prompt was too robotic. 
        # Students hated it because if they asked "What does this word mean?" 
        # or "Explain like I'm 5", the bot just said "Not found in context." 
        # I've updated this to act as an "Adaptive Tutor". It uses the textbook 
        # for facts, but is allowed to use its broader LLM vocabulary for analogies.
        
        return f"""You are an expert AI teaching assistant for a university student.
Your primary source of truth is the textbook excerpts provided below.

TEXTBOOK EXCERPTS:
{context}

STUDENT QUESTION:
{query}

INSTRUCTIONS:
1. Answer the question primarily using the facts from the TEXTBOOK EXCERPTS.
2. If the student asks for an analogy, a definition, or an 'Explain Like I'm 5', you MAY use your broader knowledge to explain the concept, but you must clearly state: "While this isn't exactly in the text..."
3. If the factual answer to a specific question is completely missing from the excerpts, state: "I couldn't find the exact answer in the textbook, but based on general knowledge..." and then provide a helpful explanation.
4. Be engaging, supportive, and educational. Do not act like a robot; act like a real tutor.
"""

    async def ask(self, query: str) -> str:
        logger.info(f"User asked: '{query}'")
        
        # 1. Retrieve relevant textbook knowledge
        logger.info("Retrieving context from Vector Store...")
        context = await self.retrieve_context(query)
        
        if not context:
            logger.warning("No context found. Is the vector database empty?")
            return "My textbook memory is empty. Did you run the ingestion script on a PDF yet?"
            
        # 2. Build the strict RAG prompt
        full_prompt = self.build_rag_prompt(query, context)
        
        # 3. Synthesize the answer
        logger.info("Synthesizing answer via Gemini...")
        response = await self.llm.generate_text(full_prompt)
        answer = response["text"]
        
        # 4. Save to conversation memory
        self.chat_history.append({"user": query, "model": answer})
        
        return answer

async def _test_engine():
    engine = TextbookRAGEngine()
    answer = await engine.ask("What is this textbook about?")
    print("\n\n=== RESPONSE ===")
    print(answer)

if __name__ == "__main__":
    asyncio.run(_test_engine())
