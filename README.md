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

---

## Future Roadmap (V3.0)
I plan to continuously upgrade these projects as I progress through my degree. Next steps:
- Converting the Chatbot's custom ML classifier into a Deep Learning Neural Network (using TensorFlow).
- Moving the Student Manager from SQLite to a cloud database (like PostgreSQL/Firebase) and serving it via a FastAPI/Flask REST API backend.

Feel free to check out the code!
