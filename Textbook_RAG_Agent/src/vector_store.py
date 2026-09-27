import os
import sys
import asyncio
import logging
from typing import List, Dict

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import chromadb

from src.document_processor import DocumentProcessor
from src.llm_client import GeminiClient

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

class TextbookVectorStore:
    def __init__(self, collection_name: str = "textbook_knowledge"):
        # Setting up local persistence. 
        # TODO(bhaskar): Remember to gitignore the data/vector_store folder! I accidentally 
        # pushed a 200MB sqlite file to github on my last project.
        db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "vector_store")
        
        # Disabling telemetry because it sometimes hangs on the university wifi.
        self.chroma_client = chromadb.PersistentClient(
            path=db_path, 
            settings=chromadb.Settings(anonymized_telemetry=False)
        )
        
        # We don't use Chroma's built-in embedding functions because we are
        # manually wiring it to our Gemini Client to maintain strict rate limit control.
        self.collection = self.chroma_client.get_or_create_collection(name=collection_name)
        
        self.doc_processor = DocumentProcessor()
        self.llm = GeminiClient()

    async def ingest_pdf(self, file_path: str):
        """
        Extracts, chunks, embeds, and stores a PDF into the local ChromaDB vector store.
        """
        logger.info(f"Starting ingestion pipeline for: {file_path}")
        
        # 1. Extraction & Chunking
        raw_text = self.doc_processor.extract_text_from_pdf(file_path)
        if not raw_text:
            logger.error("No text extracted. Aborting ingestion.")
            return
            
        chunks = self.doc_processor.chunk_document(raw_text)
        logger.info(f"Generated {len(chunks)} chunks.")
        
        # 2. Embedding generation
        # I found through trial and error that batches of 100 work best for the free API tier.
        # Anything higher sometimes throws a 400 Payload Too Large error on dense textbook pages.
        batch_size = 100
        all_embeddings = []
        
        logger.info(f"Generating embeddings in batches of {batch_size}...")
        for i in range(0, len(chunks), batch_size):
            batch_chunks = chunks[i:i + batch_size]
            
            # Using our custom async client to fetch embeddings with exponential backoff
            batch_embs = await self.llm.generate_embeddings_batch(batch_chunks)
            all_embeddings.extend(batch_embs)
            logger.info(f"Embedded batch {i//batch_size + 1}/{(len(chunks) + batch_size - 1)//batch_size}")

        if len(all_embeddings) != len(chunks):
            logger.error(f"Embedding mismatch! Expected {len(chunks)}, got {len(all_embeddings)}.")
            return
            
        # 3. Upsert to ChromaDB
        # Generate deterministic IDs based on the filename and chunk index so we don't 
        # duplicate data if we run the script twice on the same PDF.
        base_name = os.path.basename(file_path)
        ids = [f"{base_name}_chunk_{i}" for i in range(len(chunks))]
        metadatas = [{"source": base_name, "chunk_idx": i} for i in range(len(chunks))]
        
        logger.info(f"Upserting {len(chunks)} vectors to ChromaDB...")
        self.collection.upsert(
            ids=ids,
            documents=chunks,
            embeddings=all_embeddings,
            metadatas=metadatas
        )
        
        logger.info("Ingestion complete!")

async def _test_ingestion():
    test_pdf = os.path.join("data", "raw_pdfs", "sample.pdf")
    if not os.path.exists(test_pdf):
        print(f"No sample PDF found at {test_pdf}. Add one to test the pipeline.")
        return
        
    store = TextbookVectorStore()
    await store.ingest_pdf(test_pdf)

if __name__ == "__main__":
    asyncio.run(_test_ingestion())
