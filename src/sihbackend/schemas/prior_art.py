from pydantic import BaseModel
from typing import List, Tuple, Optional

class EvidenceNode(BaseModel):
    id: str
    label: str
    layer: str  # e.g., 'formulation', 'ingredient', 'tkdl', 'patent', 'international'
    source: Optional[str] = None
    jurisdiction: Optional[str] = None
    caseNumber: Optional[str] = None
    outcome: Optional[str] = None
    sourceDate: Optional[str] = None
    verification: Optional[str] = None
    passage: Optional[str] = None

class PriorArtGraphRequest(BaseModel):
    query: Optional[str] = None  # The formulation or keywords

class PriorArtGraphResponse(BaseModel):
    nodes: List[EvidenceNode]
    edges: List[Tuple[str, str]]
