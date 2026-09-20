from pydantic import BaseModel, Field
from typing import List

class FormulationRequest(BaseModel):
    product: str
    classical: str
    novelty: str
    claim: str
    route: str

class FormulationResponse(BaseModel):
    label: str = Field(description="The category (e.g. 'Cosmetic', 'Phytopharmaceutical', 'Ayurveda-Aahar / nutraceutical', 'Classical / generic Ayurvedic medicine', 'Patent / proprietary medicine')")
    confidence: int = Field(description="Confidence score from 0 to 100")
    reasoning: str = Field(description="A concise explanation based on the input answers and legal context")
    route: str = Field(description="The specific regulatory route (e.g. 'Cosmetics licensing route', 'Phytopharmaceutical drug route')")
    authorities: List[str] = Field(description="List of regulatory authorities (e.g. 'CDSCO', 'Ministry of Ayush', 'FSSAI')")
    ip: List[str] = Field(description="List of applicable IP protections (e.g. 'Trade mark', 'Process patent', 'Trade secret')")
