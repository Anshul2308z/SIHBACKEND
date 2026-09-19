import pytest
from unittest.mock import patch, MagicMock
from sihbackend.services.translation import translate_text, translate_texts

def test_translation_fallback():
    # If no client, should return original text
    with patch("sihbackend.services.translation.get_translate_client", return_value=None):
        res = translate_texts(["Hello"], "hi")
        assert res == ["Hello"]

def test_translation_success():
    mock_client = MagicMock()
    mock_client.translate.return_value = [{"translatedText": "नमस्ते"}]
    with patch("sihbackend.services.translation.get_translate_client", return_value=mock_client):
        res = translate_texts(["Hello"], "hi")
        assert res == ["नमस्ते"]
