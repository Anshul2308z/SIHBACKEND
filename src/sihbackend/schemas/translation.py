from pydantic import BaseModel, Field

class TranslationRequest(BaseModel):
    text: str = Field(..., min_length=1, description="The text to translate.")
    source_language: str = Field(default="en", description="The source language code (e.g., 'en').")
    target_language: str = Field(..., description="The target language code (e.g., 'hi', 'mr').")

class TranslationResponse(BaseModel):
    translation: str
    source_language: str
    target_language: str
    cached: bool
