import os
from dotenv import load_dotenv
import requests

load_dotenv()
api_key = os.environ.get("GROQ_API_KEY")

if not api_key:
    print("No GROQ_API_KEY found in .env")
else:
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    try:
        response = requests.get("https://api.groq.com/openai/v1/models", headers=headers)
        if response.status_code == 200:
            models = response.json().get("data", [])
            print("=== Models Available to Your Groq Key ===")
            for model in models:
                print(f"- {model['id']}")
        else:
            print(f"Failed to fetch models: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Error: {e}")
