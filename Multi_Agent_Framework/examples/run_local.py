import asyncio
import os
import sys
from dotenv import load_dotenv

# Ensure local imports work cleanly
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.core.orchestrator import Orchestrator

# Load environment variables (e.g., GEMINI_API_KEY)
load_dotenv()

async def main():
    print("Initializing Multi-Agent Framework...")
    
    # Initialize the Orchestrator with a strict 6-turn limit
    orchestrator = Orchestrator(max_turns=6)
    
    task = """
    Write a Python script that reads a CSV file called 'data.csv', 
    calculates the average of the 'price' column, and saves the result to 'output.txt'.
    """
    
    # Kick off the multi-agent team (Planner -> Worker <-> Reviewer)
    result = await orchestrator.kickoff(task)
    
    print("\n\n" + "="*40)
    print("=== FINAL APPROVED RESULT ===")
    print("="*40)
    print(result)

if __name__ == "__main__":
    # Ensure GEMINI_API_KEY is set before running
    if not os.getenv("GEMINI_API_KEY"):
        print("WARNING: GEMINI_API_KEY not found in environment variables.")
        print("Please set it or create a .env file before running.")
    else:
        asyncio.run(main())
