import os
from dotenv import load_dotenv
import requests
import json

load_dotenv()
api_key = os.environ.get("GROQ_API_KEY")

headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

payload = {
    "messages": [{"role": "user", "content": "What is the weather like in Boston?"}],
    "tools": [
        {
            "type": "function",
            "function": {
                "name": "get_current_weather",
                "description": "Get the current weather in a given location",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "location": {
                            "type": "string",
                            "description": "The city and state, e.g. San Francisco, CA",
                        },
                        "unit": {"type": "string", "enum": ["celsius", "fahrenheit"]},
                    },
                    "required": ["location"],
                },
            }
        }
    ],
    "tool_choice": "auto",
    "max_tokens": 100
}

test_models = ["qwen/qwen3.8-27b", "allam-2-7b", "openai/gpt-oss-120b", "canopylabs/orpheus-arabic-saudi"]

for model in test_models:
    payload["model"] = model
    res = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=payload)
    print(f"\n--- {model} ---")
    print(f"Status: {res.status_code}")
    print(f"Response: {res.text[:250]}")
