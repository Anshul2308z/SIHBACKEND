from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional
from datetime import datetime

class ExpertConsultationRequest(BaseModel):
    name: str = Field(..., max_length=100)
    email: EmailStr
    organization: Optional[str] = Field(None, max_length=150)
    topic: str = Field(..., max_length=100)
    context: str = Field(..., max_length=2000)

class ExpertConsultationResponse(BaseModel):
    id: int
    name: str
    created_at: datetime
    message: str = "Expert consultation request captured successfully."

    model_config = ConfigDict(from_attributes=True)
