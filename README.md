# AI, Machine Learning & Backend Engineering Portfolio

Hi! I'm **Bhaskar Bahukhandi**, a second-year B.Tech CSE (AI & ML) student at Graphic Era Deemed To Be University.

This repository houses 7 complete Python systems spanning **Generative AI & RAG**, **Deep Reinforcement Learning**, **Multi-Agent Orchestration**, **Computer Vision**, **Cloud-Native Microservices**, and **Relational Database Applications**.

---

## 1. [Automated ATS Microservice (V1.0 - Cloud-Native Microservice)](./Automated_ATS_API)
**Stack:** `Python` · `FastAPI` · `Docker Compose` · `Gemini Interactions API` · `Streamlit` · `SQLAlchemy` · `Pydantic`

A production-ready resume parser and semantic evaluator built to automate HR candidate screening. It calculates deterministic vector match scores between candidate PDF resumes and target Job Descriptions.

**Key Features & Architecture:**
- **Asynchronous FastAPI Backend:** Fully non-blocking REST API (`/evaluate-resume`, `/health`) running concurrent LLM extraction and embedding tasks via `asyncio.gather`.
- **Structured LLM Outputs:** Uses the Gemini Interactions API (`gemini-3.7-flash`) enforced by strict `Pydantic` JSON schemas and `tenacity` exponential-backoff retries (`4 attempts`, `2s–15s` wait) to survive API rate limits.
- **Deterministic Vector Math:** Computes Cosine Similarity across **768-dimensional** dense vector embeddings (`gemini-embedding-2`) to generate objective semantic match percentages.
- **Streamlit HR Dashboard:** Interactive frontend allowing recruiters to upload PDF resumes and inspect extracted skills, candidate summaries, and match scores.
- **Docker Compose Orchestration:** Multi-container setup orchestrating **2 isolated microservices** (`ats_api` on port `8000` and `ats_frontend` on port `8501`) connected over a custom `ats_network` bridge driver.
- **SQLite & SQLAlchemy ORM:** Automatically logs evaluated candidate records, parsed skill arrays, and match scores into a persistent relational database.

---

## 2. [RL Trading Bot (PPO + Optuna Hyperparameter Tuning)](./RL_Trading_Bot)
**Stack:** `Python` · `Stable-Baselines3` · `Gymnasium` · `Optuna` · `Pandas` · `NumPy`

An autonomous quantitative stock trading agent trained using Proximal Policy Optimization (PPO) and evaluated on out-of-sample market data.

**Key Features & Architecture:**
- **Custom Gymnasium Environment:** Engineered a custom OpenAI Gymnasium trading environment over **1,210 NVDA trading days**, modeling a **10-feature normalized state space** (price action, technical indicators, position state) and realistic **0.1% transaction costs**.
- **Bayesian Hyperparameter Tuning:** Integrated **Optuna** to tune PPO hyperparameters (learning rate, discount factor, GAE lambda, entropy coefficient) across **20 automated trials (300,000 total tuning timesteps)** before final policy training (**100,000 timesteps**).
- **Out-of-Sample Backtesting Engine:** Built a strict **250-trading-day out-of-sample backtest** loop to benchmark the trained PPO policy's cumulative PnL and drawdown against a passive Buy & Hold baseline.

---

## 3. [Textbook RAG Agent (Adaptive AI Study Assistant)](./Textbook_RAG_Agent)
**Stack:** `Python` · `ChromaDB` · `PyMuPDF` · `Gemini API` · `Asyncio` · `Pydantic`

An intelligent study assistant that allows university students to query their course textbooks using Retrieval-Augmented Generation (RAG) while preventing out-of-context hallucinations.

**Key Features & Architecture:**
- **Custom Document Chunker (`PyMuPDF`):** Extracts and cleans raw PDF text page-by-page, splitting dense chapters into overlapping semantic windows (**1,024-character chunks** with **128-character overlap**) snapped to word boundaries so words are never sliced mid-token.
- **Batched Async Embedding Pipeline:** Generates `gemini-embedding-2` vectors asynchronously via `asyncio.gather` in rate-limit-safe batches of **100** with exponential backoff.
- **Persistent Vector Store (`ChromaDB`):** Indexes embeddings with deterministic chunk IDs (`{filename}_chunk_{i}`) to prevent duplicate ingestion and executes **top-3 semantic retrieval**.
- **Adaptive Tutor Synthesizer:** Custom RAG system prompt that grounds factual answers strictly in retrieved textbook excerpts while permitting clearly labeled analogies for complex concepts.

---

## 4. [Multi-Agent Framework (Autonomous Agent Orchestrator)](./Multi_Agent_Framework)
**Stack:** `Python` · `Asyncio` · `FastAPI` · `Custom Event-Driven Message Bus`

An event-driven framework designed to orchestrate multiple specialized AI agents working collaboratively to plan, execute, and review complex programming and reasoning tasks.

**Key Features & Architecture:**
- **Role-Specialized Agent Triad:** Coordinates three distinct autonomous agents—**PlannerAgent** (task decomposition), **WorkerAgent** (code/tool execution), and **ReviewerAgent** (quality assurance and verification).
- **Asynchronous Pub/Sub Message Bus:** Custom `AsyncMessageBus` supporting direct agent-to-agent routing and global `broadcast` traffic monitoring without blocking the Python event loop.
- **Circuit Breaker Safety Guardrails:** Implements strict turn-limit monitoring (`max_turns = 6`) inside the central `Orchestrator` to detect infinite Worker–Reviewer debate loops and halt runaway API token consumption gracefully.
- **Tool Calling & Telemetry Logging:** Equips agents with custom Python tools (filesystem access, execution hooks) and persists session telemetry (`logs/last_run.log`) for post-run auditing.

---

## 5. [Traffic Analytics Dashboard (Real-Time YOLOv8 Computer Vision)](./Traffic_Analytics_Dashboard)
**Stack:** `Python` · `YOLOv8 (Ultralytics)` · `OpenCV` · `Streamlit` · `NumPy`

An end-to-end Computer Vision pipeline and interactive dashboard for real-time vehicle detection, multi-object tracking, and virtual tripwire traffic counting in video streams.

**Key Features & Architecture:**
- **Multi-Object Detection & Tracking (`YOLOv8`):** Utilizes `yolov8n.pt` with persistent object ID tracking (`mdl.track(persist=True)`) to track cars and heavy trucks (`class IDs 2 & 7`) across consecutive frames.
- **Centroid Tripwire Counting Engine:** Computes bounding-box centroids `(cx, cy)` per vehicle ID and tracks vertical trajectory across a calibrated horizontal tripwire line to count vehicles without double-counting across frames.
- **Automated Dataset Prep & Annotation:** Includes custom pipelines (`auto_annotate.py`, `prep_dataset.py`, `train_model.py`) for preparing custom YOLO datasets and exporting annotated `.mp4` video streams via `cv2.VideoWriter`.
- **Interactive Streamlit UI:** Visualizes live vehicle counts, frame-by-frame bounding-box overlays, and traffic density analytics.

---

## 6. [AI Chatbot (V2.0 - Custom ML & GUI Edition)](./AI_Chatbot)
**Stack:** `Python` · `Custom NLP` · `SQLite` · `Tkinter` · `pyttsx3` · `REST APIs`

A conversational AI assistant built entirely from scratch without external ML libraries, combining a custom mathematical intent classifier, dynamic knowledge fallbacks, and continual database learning.

**Key Features & Architecture:**
- **From-Scratch ML Intent Classifier:** Implemented a custom Bag-of-Words vocabulary builder, stop-word filter, and manual Cosine Similarity vector engine in pure Python to classify **15 distinct user intents** with dynamic confidence thresholding.
- **Live External API Integrations:** Queries the **Open-Meteo REST API** for live Dehradun weather telemetry and uses the **Wikipedia REST API** as a zero-shot knowledge base fallback for open-ended `"what is / who is"` queries.
- **Continual Learning Mode (`SQLite`):** When encountering an unknown prompt, the bot enters `LEARN_MODE`, prompting the user to teach it the appropriate response and persisting the new pattern into a local `chat_logs.db` (`learned` table) to dynamically expand its training set.
- **Dual CLI & Desktop GUI with TTS:** Runs in either a colorized Terminal UI (with interactive tech trivia quizzes and dynamic math evaluation) or a `Tkinter` Desktop GUI integrated with offline Text-to-Speech (`pyttsx3`).

---

## 7. [Student Data Management System (V2.0 - Relational DB Edition)](./Student_Data_Management_System)
**Stack:** `Python` · `SQLite` · `SHA-256 Auth` · `Matplotlib` · `CSV Pipelines` · `Tkinter`

A full-featured relational database application for managing university student records, fee ledgers, and academic performance analytics.

**Key Features & Architecture:**
- **Relational SQLite Schema with Foreign Keys:** Enforces `PRAGMA foreign_keys = ON` to link the primary `studs` table with a relational `fees` table using `ON DELETE CASCADE` for strict referential integrity.
- **Cryptographic Admin Authentication:** Protects system access with an admin login layer that hashes and verifies credentials using `hashlib.sha256` against the `admins` table, paired with strict regex input validation (`10-digit phone`, `RFC-style email`, semester/marks bounds).
- **Data Visualization Engine:** Integrates `matplotlib` to dynamically aggregate SQL statistics and render/export visual Bar Charts of student performance across branches and semesters.
- **Bidirectional CSV Data Pipelines:** Built an ingestion and export engine using Python's `csv` module to batch-import student rosters from spreadsheets and export full database backups.
- **Graphical Dashboard (`Tkinter`):** Provides a visual desktop interface for browsing student records and inspecting live SQL count metrics.

---

## 🗺️ Future Roadmap (V3.0)
- Deploying the containerized microservices with an automated CI/CD pipeline via **GitHub Actions**.
- Migrating local SQLite stores to a managed **PostgreSQL + pgvector** cluster on AWS/GCP.
