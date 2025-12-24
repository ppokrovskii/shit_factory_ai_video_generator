"""Unit tests for Gemini Pro image provider."""
import os
from pathlib import Path
import sys
import pytest
from unittest.mock import Mock, patch, MagicMock
from app.image_gen.gemini_pro import GeminiProImageProvider
from app.image_gen.base import ImagePrompt, ImageGenResult


@pytest.fixture
def mock_genai():
    """Mock google.generativeai module."""
    mock = MagicMock()
    sys.modules['google.generativeai'] = mock
    yield mock
    if 'google.generativeai' in sys.modules:
        del sys.modules['google.generativeai']


@pytest.mark.unit
def test_gemini_pro_init_without_api_key(monkeypatch):
    """Test that initialization fails without API key."""
    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
    
    with pytest.raises(RuntimeError, match="GOOGLE_API_KEY not set"):
        GeminiProImageProvider()


@pytest.mark.unit
def test_gemini_pro_init_with_api_key(monkeypatch, mock_genai):
    """Test initialization with API key."""
    monkeypatch.setenv("GOOGLE_API_KEY", "test-key")
    
    provider = GeminiProImageProvider()
    assert provider.api_key == "test-key"
    assert provider.model_name == "gemini-3-pro-image-preview"
    mock_genai.configure.assert_called_once_with(api_key="test-key")


@pytest.mark.unit
def test_gemini_pro_custom_model(monkeypatch, mock_genai):
    """Test custom model name from env var."""
    monkeypatch.setenv("GOOGLE_API_KEY", "test-key")
    monkeypatch.setenv("GEMINI_PRO_IMAGE_MODEL", "custom-model")
    
    provider = GeminiProImageProvider()
    assert provider.model_name == "custom-model"


@pytest.mark.unit
def test_gemini_pro_custom_model_constructor(monkeypatch, mock_genai):
    """Test custom model name via constructor."""
    monkeypatch.setenv("GOOGLE_API_KEY", "test-key")
    
    provider = GeminiProImageProvider(model_name="constructor-model")
    assert provider.model_name == "constructor-model"


@pytest.mark.unit
def test_normalize_size_1k(monkeypatch, mock_genai):
    """Test size normalization for 1K."""
    monkeypatch.setenv("GOOGLE_API_KEY", "test-key")
    
    provider = GeminiProImageProvider()
    assert provider._normalize_size("1K") == "1024x1024"
    assert provider._normalize_size("1k") == "1024x1024"


@pytest.mark.unit
def test_normalize_size_2k(monkeypatch, mock_genai):
    """Test size normalization for 2K."""
    monkeypatch.setenv("GOOGLE_API_KEY", "test-key")
    
    provider = GeminiProImageProvider()
    assert provider._normalize_size("2K") == "2048x2048"
    assert provider._normalize_size("2k") == "2048x2048"


@pytest.mark.unit
def test_normalize_size_4k(monkeypatch, mock_genai):
    """Test size normalization for 4K."""
    monkeypatch.setenv("GOOGLE_API_KEY", "test-key")
    
    provider = GeminiProImageProvider()
    assert provider._normalize_size("4K") == "4096x4096"
    assert provider._normalize_size("4k") == "4096x4096"


@pytest.mark.unit
def test_normalize_size_passthrough(monkeypatch, mock_genai):
    """Test that non-shorthand sizes pass through."""
    monkeypatch.setenv("GOOGLE_API_KEY", "test-key")
    
    provider = GeminiProImageProvider()
    assert provider._normalize_size("1024x768") == "1024x768"
    assert provider._normalize_size("16:9") == "16:9"


@pytest.mark.unit
def test_generate_images_skip_existing(tmp_path, monkeypatch, mock_genai):
    """Test that existing images are skipped."""
    monkeypatch.setenv("GOOGLE_API_KEY", "test-key")
    
    # Create existing image
    existing_file = tmp_path / "test.png"
    existing_file.write_text("existing")
    
    provider = GeminiProImageProvider()
    
    prompt = ImagePrompt(
        index=0,
        code="test",
        positive_prompt="test prompt",
        target_filename="test.png",
    )
    
    results = provider.generate_images([prompt], tmp_path, skip_existing=True)
    
    assert len(results) == 1
    assert results[0].path == existing_file
    assert existing_file.read_text() == "existing"  # Not overwritten


@pytest.mark.unit
def test_generate_images_basic(tmp_path, monkeypatch, mock_genai):
    """Test basic image generation."""
    monkeypatch.setenv("GOOGLE_API_KEY", "test-key")
    
    # Mock the model and response
    mock_model = MagicMock()
    mock_genai.GenerativeModel.return_value = mock_model
    
    # Create mock response with image data
    mock_part = MagicMock()
    mock_part.inline_data = MagicMock()
    mock_part.inline_data.data = b"fake image data" * 100  # Make it > 1KB
    
    mock_candidate = MagicMock()
    mock_candidate.content.parts = [mock_part]
    
    mock_response = MagicMock()
    mock_response.candidates = [mock_candidate]
    
    mock_model.generate_content.return_value = mock_response
    
    provider = GeminiProImageProvider()
    
    prompt = ImagePrompt(
        index=0,
        code="test",
        positive_prompt="test prompt",
        target_filename="test.png",
    )
    
    results = provider.generate_images([prompt], tmp_path, skip_existing=False)
    
    assert len(results) == 1
    assert results[0].path == tmp_path / "test.png"
    assert results[0].path.exists()
    mock_model.generate_content.assert_called_once()


@pytest.mark.unit
def test_generate_images_with_size_parameter(tmp_path, monkeypatch, mock_genai):
    """Test image generation with custom size."""
    monkeypatch.setenv("GOOGLE_API_KEY", "test-key")
    
    mock_model = MagicMock()
    mock_genai.GenerativeModel.return_value = mock_model
    
    # Mock response with image
    mock_part = MagicMock()
    mock_part.inline_data = MagicMock()
    mock_part.inline_data.data = b"fake image data" * 100
    
    mock_candidate = MagicMock()
    mock_candidate.content.parts = [mock_part]
    
    mock_response = MagicMock()
    mock_response.candidates = [mock_candidate]
    
    mock_model.generate_content.return_value = mock_response
    
    provider = GeminiProImageProvider()
    
    prompt = ImagePrompt(
        index=0,
        code="test",
        positive_prompt="test prompt",
        target_filename="test.png",
    )
    
    # Test with 4K size
    results = provider.generate_images([prompt], tmp_path, size="4K", skip_existing=False)
    
    assert len(results) == 1
    assert results[0].path.exists()


@pytest.mark.unit
def test_generate_images_with_negative_prompt(tmp_path, monkeypatch, mock_genai):
    """Test that negative prompts are included in generation."""
    monkeypatch.setenv("GOOGLE_API_KEY", "test-key")
    
    mock_model = MagicMock()
    mock_genai.GenerativeModel.return_value = mock_model
    
    # Mock response
    mock_part = MagicMock()
    mock_part.inline_data = MagicMock()
    mock_part.inline_data.data = b"fake image data" * 100
    
    mock_candidate = MagicMock()
    mock_candidate.content.parts = [mock_part]
    
    mock_response = MagicMock()
    mock_response.candidates = [mock_candidate]
    
    mock_model.generate_content.return_value = mock_response
    
    provider = GeminiProImageProvider()
    
    prompt = ImagePrompt(
        index=0,
        code="test",
        positive_prompt="a cat",
        negative_prompt="blurry, low quality",
        target_filename="test.png",
    )
    
    results = provider.generate_images([prompt], tmp_path, skip_existing=False)
    
    # Check that generate_content was called
    assert mock_model.generate_content.called
    call_args = mock_model.generate_content.call_args[0][0]
    
    # The prompt should contain both positive and negative
    assert isinstance(call_args, list)
    assert "a cat" in call_args[0]
    assert "Avoid:" in call_args[0]
    assert "blurry, low quality" in call_args[0]


@pytest.mark.unit
def test_generate_images_handles_empty_response(tmp_path, monkeypatch, mock_genai):
    """Test handling of empty response from API."""
    monkeypatch.setenv("GOOGLE_API_KEY", "test-key")
    
    mock_model = MagicMock()
    mock_genai.GenerativeModel.return_value = mock_model
    
    # Mock empty response
    mock_response = MagicMock()
    mock_response.candidates = []
    
    mock_model.generate_content.return_value = mock_response
    
    provider = GeminiProImageProvider()
    
    prompt = ImagePrompt(
        index=0,
        code="test",
        positive_prompt="test prompt",
        target_filename="test.png",
    )
    
    results = provider.generate_images([prompt], tmp_path, skip_existing=False)
    
    assert len(results) == 1
    # File should not exist (generation failed)
    assert not results[0].path.exists()

