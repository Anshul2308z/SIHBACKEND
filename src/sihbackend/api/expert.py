from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sihbackend.db.database import get_db
from sihbackend.db.models import ExpertConsultation
from sihbackend.schemas.expert import ExpertConsultationRequest, ExpertConsultationResponse

router = APIRouter(prefix="/api/v1/expert", tags=["Expert"])

@router.post("/consultation", response_model=ExpertConsultationResponse)
async def submit_consultation(request: ExpertConsultationRequest, db: Session = Depends(get_db)):
    db_consultation = ExpertConsultation(
        name=request.name,
        email=request.email,
        organization=request.organization,
        topic=request.topic,
        context=request.context
    )
    db.add(db_consultation)
    db.commit()
    db.refresh(db_consultation)
    
    return ExpertConsultationResponse(
        id=db_consultation.id,
        name=db_consultation.name,
        created_at=db_consultation.created_at,
        message="Expert consultation request captured successfully."
    )
