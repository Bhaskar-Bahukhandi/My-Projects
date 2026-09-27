import requests

# Quick scratch script to test if the API is working locally 
# before we bother building the Streamlit frontend.

BASE_URL = "http://127.0.0.1:8000"

def run_tests():
    try:
        print("Pinging root endpoint (GET /)...")
        response = requests.get(f"{BASE_URL}/")
        print("Status Code:", response.status_code)
        print("Response:", response.json())
        
        print("\nPinging health endpoint (GET /health)...")
        health = requests.get(f"{BASE_URL}/health")
        print("Status Code:", health.status_code)
        print("Health Check:", health.json())
        
    except requests.exceptions.ConnectionError:
        print("\n[ERROR] Connection refused!")
        print("Is the FastAPI server running?")
        print("Make sure to run this command in a separate terminal first:")
        print("  uvicorn src.main:app --reload")

if __name__ == "__main__":
    run_tests()
