from pydantic import BaseModel, Field
from typing import Optional, List

class AnalysisRequest(BaseModel):
    query: str = Field(..., min_length=1, description="The query to analyze against the legal corpus.")

class AnalysisResponse(BaseModel):
    answer: str
    risk_level: Optional[str]
    key_requirements: List[str]
    relevant_jurisdictions: List[str]
    sources: List[str]
    caveats: List[str]
