import os
import sys
import asyncio
import streamlit as st

# Allow local imports so we don't have to fiddle with the PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.rag_engine import TextbookRAGEngine
from src.vector_store import TextbookVectorStore

# Streamlit Page Config
st.set_page_config(page_title="Textbook RAG", page_icon="📚", layout="wide")

# --- STATE MANAGEMENT ---
# Streamlit literally reruns the entire python script from top to bottom on every click. 
# Stashing the engine and vector store in session_state prevents us from 
# rebuilding the ChromaDB connection every single time the user types a letter.
if "engine" not in st.session_state:
    st.session_state.engine = TextbookRAGEngine()
    
if "vector_store" not in st.session_state:
    st.session_state.vector_store = TextbookVectorStore()

if "messages" not in st.session_state:
    st.session_state.messages = []

# --- UI LAYOUT ---
st.title("📚 Chat-with-your-Textbook RAG")
st.markdown("Upload a PDF textbook and ask questions. The AI will answer strictly based on the text.")

# --- SIDEBAR: Document Uploader ---
with st.sidebar:
    st.header("1. Upload Textbook")
    uploaded_file = st.file_uploader("Upload a PDF file", type=["pdf"])
    
    if uploaded_file is not None:
        if st.button("Process & Index PDF"):
            with st.spinner("Extracting and Embedding PDF... This might take a minute."):
                # TODO(bhaskar): The file uploader blocks the main UI thread during PDF chunking.
                # For a 1000-page textbook, this UI will completely freeze. I need to move ingestion 
                # to a background worker (like Celery or RQ) for V2 of this portfolio project.
                
                # Save uploaded file to a local staging directory
                temp_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "raw_pdfs")
                os.makedirs(temp_dir, exist_ok=True)
                temp_path = os.path.join(temp_dir, uploaded_file.name)
                
                with open(temp_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                
                # Run the async ingestion pipeline synchronously for Streamlit
                asyncio.run(st.session_state.vector_store.ingest_pdf(temp_path))
                st.success(f"Indexed '{uploaded_file.name}' successfully!")

# --- MAIN CHAT UI ---
st.header("2. Ask Questions")

# Render existing chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# User Input
if prompt := st.chat_input("Ask a question about the textbook (e.g., 'What are the main causes of the revolution?'):"):
    # Display user's prompt
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Fetch and display Assistant's RAG response
    with st.chat_message("assistant"):
        with st.spinner("Searching textbook memory..."):
            # Streamlit is synchronous, but our backend is async. 
            # We use asyncio.run to bridge the gap.
            response_text = asyncio.run(st.session_state.engine.ask(prompt))
            st.markdown(response_text)
            
    # Save assistant's response to history
    st.session_state.messages.append({"role": "assistant", "content": response_text})
