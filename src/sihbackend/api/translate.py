from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sihbackend.schemas.translation import TranslationRequest, TranslationResponse
from sihbackend.services.translation import perform_translation
from sihbackend.db.database import get_db

router = APIRouter(prefix="/api/v1", tags=["Translation"])

@router.post("/translate", response_model=TranslationResponse)
def translate_text(request: TranslationRequest, db: Session = Depends(get_db)):
    try:
        result = perform_translation(
            db=db,
            text=request.text,
            target_language=request.target_language,
            source_language=request.source_language
        )
        return TranslationResponse(**result)
    except ValueError as ve:
        raise HTTPException(status_code=503, detail=str(ve))
    except RuntimeError as re:
        raise HTTPException(status_code=502, detail=str(re))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal Server Error")
