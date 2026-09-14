from fastapi import APIRouter
from sihbackend.schemas.analysis import AnalysisRequest, AnalysisResponse
from sihbackend.services.analysis import perform_analysis

router = APIRouter(prefix="/api/v1", tags=["Analysis"])

@router.post("/analyze", response_model=AnalysisResponse)
def analyze(request: AnalysisRequest):
    return perform_analysis(request)
