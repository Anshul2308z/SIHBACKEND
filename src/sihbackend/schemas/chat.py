from pydantic import BaseModel
from typing import List, Optional
from sihbackend.schemas.prior_art import PriorArtGraphResponse

class ChatRequest(BaseModel):
    query: str
    jurisdiction: Optional[str] = "India"
    language: Optional[str] = "en"

class EvidenceItem(BaseModel):
    id: str
    number: str
    jurisdiction: str
    risk: str
    title: str
    whyRelevant: str

class ChatResponse(BaseModel):
    executive_answer: str
    confidence: int
    source_agreement: int
    jurisdiction_coverage: int
    evidence_count: int
    applicable_ip_types: List[str]
    key_findings: List[str]
    next_steps: List[str]
    evidence: List[EvidenceItem]
    prior_art_graph: Optional[PriorArtGraphResponse] = None
