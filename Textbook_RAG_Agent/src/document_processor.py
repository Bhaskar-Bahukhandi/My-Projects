import os
import sys
import re
import logging
import pymupdf  # PyMuPDF
from typing import List

# Allow script execution from the root project directory
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.settings import config

logger = logging.getLogger(__name__)

class DocumentProcessor:
    def __init__(self, chunk_size: int = None, chunk_overlap: int = None):
        # Fall back to settings if not explicitly passed during instantiation
        self.chunk_size = chunk_size or config.chunk_size
        self.chunk_overlap = chunk_overlap or config.chunk_overlap

    def clean_text(self, text: str) -> str:
        """
        Strips out wild OCR artifacts and rogue newlines.
        """
        # Textbooks usually have weird line breaks from PDF formatting.
        # This regex just squashes multiple newlines and spaces.
        text = re.sub(r'\n+', '\n', text)
        text = re.sub(r'\s+', ' ', text)
        return text.strip()

    def extract_text_from_pdf(self, file_path: str) -> str:
        """
        Reads a PDF page-by-page using PyMuPDF and extracts all raw text.
        """
        logger.info(f"Loading PDF: {file_path}")
        try:
            doc = pymupdf.open(file_path)
            full_text = ""
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                full_text += page.get_text("text") + "\n"
                
            doc.close()
            return self.clean_text(full_text)
            
        except Exception as e:
            # TODO(bhaskar): Add a check here for encrypted/password-protected PDFs.
            # PyMuPDF crashes hard on those.
            logger.error(f"Failed to read PDF {file_path}. Error: {e}")
            return ""

    def chunk_document(self, text: str) -> List[str]:
        """
        Splits a massive string into overlapping semantic chunks.
        """
        if not text:
            return []
            
        # TODO(bhaskar): Currently doing character-based chunking. 
        # If the LLM starts hallucinating because sentences are getting cut in half,
        # we might need to swap this to a proper NLP sentence-splitter (like NLTK/spacy), 
        # but I am avoiding those heavy dependencies for now.
        
        chunks = []
        start = 0
        text_length = len(text)
        
        while start < text_length:
            end = start + self.chunk_size
            
            # If we're not at the very end of the document, try to snap to a space
            # so we don't slice a word directly in half.
            if end < text_length:
                last_space = text.rfind(" ", start, end)
                if last_space != -1:
                    end = last_space
            
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            
            # Slide the window forward, minus our overlap to retain context
            next_start = end - self.chunk_overlap
            
            # Failsafe to prevent infinite loops if overlap is misconfigured
            if next_start <= start:
                next_start = end
                
            start = next_start
                
        return chunks

if __name__ == "__main__":
    # Quick sanity check
    test_pdf = os.path.join("data", "raw_pdfs", "sample.pdf")
    
    if not os.path.exists(test_pdf):
        print(f"\n[!] Please drop a PDF file at {test_pdf} to test the chunker.\n")
    else:
        processor = DocumentProcessor()
        text = processor.extract_text_from_pdf(test_pdf)
        chunks = processor.chunk_document(text)
        
        print(f"Extraction successful: {len(text)} total characters.")
        print(f"Generated {len(chunks)} overlapping chunks.")
        
        if chunks:
            print("\n--- Snippet of Chunk [0] ---")
            # Just printing the first 200 chars so we don't flood the terminal
            print(chunks[0][:200] + "...")
