from sqlalchemy import Column, Integer, String, DateTime, JSON
from sqlalchemy.dialects import postgresql
from sqlalchemy.sql import func
from sihbackend.db.database import Base

JSON_TYPE = JSON().with_variant(postgresql.JSONB, 'postgresql')

class ChatHistory(Base):
    __tablename__ = "chat_history"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True, nullable=True) # Optional ownership
    query = Column(String, nullable=False)
    jurisdiction = Column(String, nullable=False, default="India")
    language = Column(String, nullable=False, default="en")
    response = Column(JSON_TYPE, nullable=False) # Stores ChatResponse
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class ExpertConsultation(Base):
    __tablename__ = "expert_consultations"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    organization = Column(String, nullable=True)
    topic = Column(String, nullable=False)
    context = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
