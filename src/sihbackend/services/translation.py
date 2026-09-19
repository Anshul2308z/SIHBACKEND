import os
import hashlib
from typing import List, Dict
from google.cloud import translate_v2 as translate
from fastapi import HTTPException
import logging

logger = logging.getLogger(__name__)

# Initialize client globally but lazily
_translate_client = None

def get_translate_client():
    global _translate_client
    if _translate_client is None:
        try:
            # Requires GOOGLE_APPLICATION_CREDENTIALS environment variable
            _translate_client = translate.Client()
        except Exception as e:
            logger.warning(f"Google Cloud Translate client not initialized: {e}")
    return _translate_client

def translate_texts(texts: List[str], target_language: str, db=None) -> List[str]:
    """Translate a list of texts into the target language without caching.
    'db' parameter is ignored but kept for signature compatibility."""
    if not texts:
        return []
        
    client = get_translate_client()
    if not client:
        # Fallback if API not configured
        return texts
        
    try:
        results = client.translate(texts, target_language=target_language)
        return [result['translatedText'] for result in results]
    except Exception as e:
        logger.error(f"Translation API error: {e}")
        return texts  # Fallback to original text

def translate_text(text: str, target_language: str, db=None) -> str:
    """Translate a single string."""
    results = translate_texts([text], target_language)
    return results[0] if results else text

def perform_translation(text: str, target_language: str, source_language: str = None, db=None) -> Dict:
    """Entrypoint for the API router."""
    translated = translate_text(text, target_language, db)
    return {
        "original_text": text,
        "translated_text": translated,
        "source_language": source_language or "auto",
        "target_language": target_language
    }
