# My Python Projects - V2.0 Major Update!

Hi! I'm **Bhaskar Bahukhandi**, a second-year (3rd semester) BTech CSE (AI & ML) student at Graphic Era Deemed University. 

This repository contains my core Python projects. Over the last few months, I have completely rewritten and upgraded them from simple scripts into robust, secure, and interactive systems.

---

## 1. AI Chatbot (V2.0 - GUI & ML Edition)
A conversational AI chatbot built entirely from scratch. I originally built this using simple keyword matching, but I upgraded it to use a **Custom Machine Learning Intent Classifier** and a full Graphical User Interface.

**Key Features & Architecture:**
- **Custom ML Classifier:** Implemented a Bag-of-Words text vectorizer and a Cosine Similarity algorithm from scratch to classify intents, complete with a strict >25% confidence threshold logic.
- **Live API Integration:** Uses the `requests` library to ping the Open-Meteo REST API, fetching live real-time weather data for Dehradun!
- **Text-to-Speech (TTS):** Integrated `pyttsx3` so the bot physically speaks its responses aloud.
- **Database Logging:** All chat history is permanently logged to a local SQLite database in real-time.
- **Dual Interface:** Runs in either a colorized Terminal UI (with simulated thinking delays) or a custom `tkinter` Desktop GUI window.

## 2. Student Data Management System (V2.0 - Relational DB Edition)
A comprehensive backend application for managing university student records. I upgraded this from a flat JSON file script into a secure, relational database application.

**Key Features & Architecture:**
- **Relational SQLite Database:** Uses `PRAGMA foreign_keys` to link a primary `studs` table to a secondary `fees` table (implementing `ON DELETE CASCADE` for data integrity).
- **Admin Authentication:** Secured the dashboard with an admin login system that encrypts passwords using `SHA-256` hashing.
- **Data Visualization:** Integrates `matplotlib` to dynamically aggregate database statistics and render/export visual Bar Charts of student performance.
- **CSV Data Pipelines:** Built a data ingestion/export engine using the `csv` module to seamlessly import data from Excel spreadsheets and export database dumps.
- **Graphical Dashboard:** Features a clean `tkinter` GUI mode for visually loading records and viewing quick SQL count statistics.

## 3. Automated ATS API (V1.0 - Cloud Native Microservice)
A production-ready resume parser and evaluator built to automate HR screening. It calculates a semantic vector match score between a candidate's PDF resume and a Job Description.
**Key Features & Architecture:**
- **FastAPI Backend:** Fully asynchronous REST API designed for high-performance concurrent processing.
- **Gemini 3.7 Flash:** Uses the state-of-the-art Interactions API and Structured Outputs (Pydantic) to extract deterministic candidate profiles in JSON format from raw PDF text.
- **Vector Math:** Calculates Cosine Similarity dynamically using dense vector embeddings (gemini-embedding-2).
- **Streamlit Frontend:** A sleek interactive dashboard for HR to upload resumes and visually inspect the extracted skills and match percentage.
- **Docker Orchestration:** Containerized with a multi-service `docker-compose.yml` for isolated frontend and backend environments.
- **SQLite/SQLAlchemy Database:** Automatically logs evaluated candidate profiles into a relational database.

## 4. Traffic Analytics Dashboard
An advanced Computer Vision dashboard for real-time traffic monitoring and vehicle detection.
**Key Features & Architecture:**
- **Computer Vision:** Employs OpenCV and YOLO for real-time object detection and tracking in video streams.
- **Real-Time UI:** Streamlit interface to visualize traffic counts, density metrics, and frame-by-frame analysis.
- **Data Engineering:** Processes and logs high-velocity data points from video sources for downstream statistical analysis.

## 5. Textbook RAG Agent
An intelligent study assistant that allows users to "chat" with their course textbooks using Retrieval-Augmented Generation (RAG).
**Key Features & Architecture:**
- **Vector Database:** Uses ChromaDB for highly efficient similarity search across textbook chunks.
- **Chunking & Embeddings:** Implements LangChain for intelligent document splitting and dense vector embeddings.
- **LLM Integration:** Leverages generative AI for contextual question-answering strictly grounded in the uploaded textbook material.

## 6. RL Trading Bot
An autonomous stock trading bot trained using Deep Reinforcement Learning.
**Key Features & Architecture:**
- **Deep Q-Learning (DQN):** Uses PyTorch/TensorFlow to train an agent to maximize financial rewards based on historical market data.
- **Backtesting Engine:** Custom evaluation loop to benchmark the agent's PnL against a hold-and-wait strategy.
- **Data Pipelines:** Ingests and normalizes live market candlestick data for continuous learning.

## 7. Multi-Agent Framework
An experimental framework designed to orchestrate multiple specialized AI agents working together to solve complex tasks.
**Key Features & Architecture:**
- **Agent Orchestration:** Custom python engine to handle task delegation, message passing, and state management between sub-agents.
- **Tool Calling:** Empowers agents with custom Python tools (file system access, API calls) to execute autonomous workflows.

---

## Future Roadmap (V3.0)
I plan to continuously upgrade these projects as I progress through my degree. Next steps:
- Deploying the entire monorepo as a single automated CI/CD pipeline via GitHub Actions.
- Migrating local SQLite databases to a managed PostgreSQL cluster on AWS/GCP.
- Entering these architectures into college hackathons!

Feel free to check out the code!
