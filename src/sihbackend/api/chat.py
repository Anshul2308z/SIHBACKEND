from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sihbackend.db.database import get_db
from sihbackend.db.models import ChatHistory
from sihbackend.schemas.chat import ChatRequest, ChatResponse
from sihbackend.services.chat_service import build_chat_response

router = APIRouter(prefix="/api/v1/chat", tags=["Chat"])

@router.post("/message", response_model=ChatResponse)
def chat_message(request: ChatRequest, db: Session = Depends(get_db)):
    # 1. Generate response
    response_data = build_chat_response(request.query, request.jurisdiction, request.language)
    
    # 2. Log to database
    chat_log = ChatHistory(
        user_id=None,  # Anonymous for now
        query=request.query,
        jurisdiction=request.jurisdiction,
        language=request.language,
        response=response_data.model_dump()
    )
    db.add(chat_log)
    db.commit()
    
    # 3. Return payload
    return response_data
