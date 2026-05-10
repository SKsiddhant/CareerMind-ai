import requests
import json
import time

BASE_URL = "http://127.0.0.1:8002"

def test_api():
    print("--- Testing CareerMind AI Backend ---")
    
    # 1. Test Root
    try:
        r = requests.get(f"{BASE_URL}/")
        print(f"Root Status: {r.status_code}")
        print(f"Response: {r.json()}\n")
    except Exception as e:
        print(f"Root Test Failed: {e}")
        return

    # 2. Test Tailoring Strategy
    print("Testing Strategy Generation (Gemini-powered)...")
    payload = {"query": "software engineer artificial intelligence"}
    try:
        r = requests.post(f"{BASE_URL}/tailor/strategy", json=payload, timeout=120)
        print(f"Strategy Status: {r.status_code}")
        if r.status_code == 200:
            print("🚀 GOATed Strategy Results:")
            print(json.dumps(r.json(), indent=4))
        else:
            print(f"Error: {r.text}")
    except Exception as e:
        print(f"Strategy Test Failed: {e}")

    # 3. Test Interview Coach
    print("\nTesting Interview Coach Evaluation...")
    interview_payload = {
        "job_title": "AI Engineer",
        "question": "How do you handle hallucinations in RAG?",
        "answer": "I use semantic validation and cross-encoding to ensure the answer matches the source context."
    }
    try:
        r = requests.post(f"{BASE_URL}/interview/evaluate", json=interview_payload, timeout=120)
        print(f"Interview Status: {r.status_code}")
        if r.status_code == 200:
            print("🎬 GOATed Interview Evaluation:")
            print(json.dumps(r.json(), indent=4))
        else:
            print(f"Error: {r.text}")
    except Exception as e:
        print(f"Interview Test Failed: {e}")

    # 4. Test Salary Negotiator
    print("\nTesting Salary Negotiator...")
    salary_payload = {
        "company": "OpenAI",
        "role": "AI Engineer",
        "match_score": 88
    }
    try:
        r = requests.post(f"{BASE_URL}/salary/negotiate", json=salary_payload, timeout=120)
        print(f"Negotiation Status: {r.status_code}")
        if r.status_code == 200:
            print("💰 Elite Negotiation Strategy:")
            print(json.dumps(r.json(), indent=4))
        else:
            print(f"Error: {r.text}")
    except Exception as e:
        print(f"Negotiation Test Failed: {e}")

if __name__ == "__main__":
    test_api()
