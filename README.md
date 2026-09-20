# My Python Projects

Hi! I'm **Bhaskar Bahukhandi**, a second-year (3rd semester) BTech CSE (AI & ML) student at Graphic Era Deemed University. 

This repository contains some of my Python projects. I'm actively building these to practice backend architecture, databases, and actual machine learning algorithms from scratch.

---

## 1. AI Chatbot (Custom Machine Learning Edition)
A conversational terminal-based chatbot. I originally built this using simple keyword matching, but I recently upgraded it to use a **Custom Machine Learning Intent Classifier** that I wrote entirely from scratch without relying on external libraries like `scikit-learn`!

**What it does & How it works:**
- I implemented a custom **Bag-of-Words** text vectorizer to convert training sentences into numerical arrays.
- I wrote a **Cosine Similarity** algorithm (calculating the dot product and magnitudes) to classify user input against 10 different intents.
- It can handle greetings, tell jokes, give tech facts, calculate math, run a quiz, and answer basic questions.

## 2. Student Data Management System (SQLite Edition)
A console-based CRUD application that manages student records. 

**What it does & How it works:**
- Connects to a local **SQLite3 database** to persistently store data.
- I wrote custom SQL queries (`INSERT`, `SELECT`, `UPDATE`, `DELETE`) to handle all backend operations instead of relying on simple text files.
- Features robust input validation (phone numbers, marks, semesters).
- Includes a statistics engine that calculates average marks, highest scorers, and branch-wise distributions dynamically from the SQL data.

---

## Future Roadmap
I plan to continuously upgrade these projects as I progress through my degree. Some things I want to add in the near future:
- Converting the Chatbot's custom ML classifier into a Neural Network (using PyTorch/TensorFlow).
- Moving the Student Manager from SQLite to a cloud database (like PostgreSQL or Firebase) with a proper REST API.
- Adding Graphical User Interfaces (GUIs) instead of just using the terminal.

Feel free to check out the code!
