from pydantic import BaseModel
from typing import List, Literal, Optional

class PatentSearchRequest(BaseModel):
    query: str
    scope: Literal["Both", "India", "International"] = "Both"
    type: Literal["Semantic", "Hybrid", "Exact"] = "Semantic"
    activeSources: List[str] = []
    plant: str = "All"
    status: str = "All"

class PatentRecord(BaseModel):
    id: str
    number: str
    title: str
    applicant: str
    jurisdiction: str
    jurisdictionGroup: str
    published: str
    similarity: int
    status: str
    risk: str
    whyRelevant: str
    concepts: List[str]
    sources: List[str]
    plants: List[str]
    family: str
    indication: str
    ipType: str
    evidenceLevel: str
