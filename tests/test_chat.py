import asyncio
from sihbackend.schemas.chat import ChatRequest
from sihbackend.services.chat_service import build_chat_response

def run():
    print("Starting chat search")
    try:
        res = build_chat_response("neem patent", "India")
        print("Success:", res.executive_answer)
    except Exception as e:
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    run()
