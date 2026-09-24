import os
import time
from dotenv import load_dotenv
load_dotenv()

from fastapi.testclient import TestClient
from sihbackend.main import app

client = TestClient(app)

TEST_CASES = [
    {
        "id": 1,
        "type": "EXACT / NEAR-EXACT MATCH",
        "query": "A traditional Ayurvedic formulation using Turmeric (Curcuma longa) and Neem (Azadirachta indica) for wound healing and skin infections.",
    },
    {
        "id": 4,
        "type": "NO MATCH",
        "query": "A therapeutic extract of Ginkgo Biloba and Maca root for enhancing deep space radiation resistance in astronauts.",
    },
    {
        "id": 6,
        "type": "WRONG DOCUMENT TYPE (Legal query)",
        "query": "What are the packaging and labeling requirements for a new Ashwagandha Ayurveda-Aahar product?",
    },
    {
        "id": 8,
        "type": "TKDL VS PATENT EVIDENCE",
        "query": "Is there prior art for using Amla (Phyllanthus emblica) for Vitamin C deficiency?",
    },
    {
        "id": 10,
        "type": "FABRICATION / ABSTENTION",
        "query": "What is the exact patent number and applicant name for the 2018 patent covering Ashwagandha used in lithium-ion smartphone batteries?",
    }
]

def run_tests():
    print("--- IP-SAKTI Sahayak AI Assistant Automated QA ---\n")
    for tc in TEST_CASES:
        if tc['id'] not in [1, 4, 6]:
            continue
            
        print(f"==================================================")
        print(f"TEST CASE {tc['id']} [{tc['type']}]")
        print(f"INPUT: {tc['query']}")
        
        response = client.post("/api/v1/chat/message", json={
            "query": tc['query'],
            "jurisdiction": "India",
            "language": "en"
        })
        
        if response.status_code == 200:
            data = response.json()
            print(f"\nACTUAL CONFIDENCE: {data.get('confidence')}%")
            print(f"ACTUAL OUTPUT:\n{data.get('executive_answer')}")
            print(f"\nEVIDENCE RETRIEVED: {data.get('evidence_count')} documents")
        else:
            print(f"Failed with status code {response.status_code}: {response.text}")
        print("\n")
        
        # Prevent LLM API Rate Limits (Google Free Tier = 5 RPM, Groq = 1000 OTPM)
        if tc != TEST_CASES[-1]:
            print("Sleeping for 15 seconds to respect LLM rate limits...\n")
            time.sleep(15)

if __name__ == "__main__":
    run_tests()