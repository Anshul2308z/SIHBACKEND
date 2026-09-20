from pydantic import BaseModel, Field
from typing import List, Literal

class AbsRequest(BaseModel):
    resource: str
    origin: str
    collection: str
    tk: bool
    commercial: bool
    patent: bool
    exportMarket: bool

class AbsStatus(BaseModel):
    level: Literal["risk", "review", "verified"] = Field(description="'risk' if documentation/approval is definitely required, 'review' if possible, 'verified' if low concern.")
    label: str = Field(description="Short human-readable label e.g., 'High — documentation likely required'")

class AbsResponse(BaseModel):
    status: AbsStatus
    framework: List[str] = Field(description="Applicable laws, e.g. ['Biological Diversity Act, 2002', 'Nagoya Protocol']")
    reasoning: str = Field(description="Detailed explanation of why ABS approval is or isn't required based on the legal context.")
