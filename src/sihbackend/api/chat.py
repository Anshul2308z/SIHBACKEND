from fastapi import APIRouter
from sihbackend.schemas.chat import ChatRequest, ChatResponse
from sihbackend.services.chat_service import build_chat_response

router = APIRouter(prefix="/api/v1/chat", tags=["Chat"])

@router.post("/message", response_model=ChatResponse)
async def chat_message(request: ChatRequest):
    return build_chat_response(request.query, request.jurisdiction)
