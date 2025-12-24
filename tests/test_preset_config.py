"""Unit tests for preset configuration loading."""
import os
import pytest
from app.preset_config import (
    load_image_preset,
    load_video_preset,
    get_default_model_for_provider,
    ImagePresetConfig,
    VideoPresetConfig,
)


@pytest.mark.unit
def test_load_image_preset_fast_default():
    """Test loading fast preset with default values."""
    config = load_image_preset("fast")
    assert config.provider == "openai"
    assert config.model == "gpt-image-1-mini"
    assert config.size == "1024x1024"


@pytest.mark.unit
def test_load_image_preset_regular_default():
    """Test loading regular preset with default values."""
    config = load_image_preset("regular")
    assert config.provider == "gemini"
    assert config.model == "gemini-2.5-flash-image"
    assert config.size == "1024x1024"


@pytest.mark.unit
def test_load_image_preset_ultra_default():
    """Test loading ultra preset with default values."""
    config = load_image_preset("ultra")
    assert config.provider == "gemini-pro"
    assert config.model == "gemini-3-pro-image-preview"
    assert config.size == "2K"


@pytest.mark.unit
def test_load_image_preset_case_insensitive():
    """Test that preset names are case-insensitive."""
    config1 = load_image_preset("FAST")
    config2 = load_image_preset("Fast")
    config3 = load_image_preset("fast")
    
    assert config1.provider == config2.provider == config3.provider
    assert config1.model == config2.model == config3.model


@pytest.mark.unit
def test_load_image_preset_invalid_name():
    """Test that invalid preset name raises ValueError."""
    with pytest.raises(ValueError, match="Unknown image preset"):
        load_image_preset("invalid")


@pytest.mark.unit
def test_load_image_preset_env_override(monkeypatch):
    """Test that environment variables override defaults."""
    monkeypatch.setenv("IMAGE_PRESET_FAST_PROVIDER", "google")
    monkeypatch.setenv("IMAGE_PRESET_FAST_MODEL", "custom-model")
    monkeypatch.setenv("IMAGE_PRESET_FAST_SIZE", "512x512")
    
    config = load_image_preset("fast")
    assert config.provider == "google"
    assert config.model == "custom-model"
    assert config.size == "512x512"


@pytest.mark.unit
def test_load_image_preset_partial_env_override(monkeypatch):
    """Test that env vars can override individual fields."""
    monkeypatch.setenv("IMAGE_PRESET_REGULAR_SIZE", "2048x2048")
    
    config = load_image_preset("regular")
    assert config.provider == "gemini"  # Default
    assert config.model == "gemini-2.5-flash-image"  # Default
    assert config.size == "2048x2048"  # Overridden


@pytest.mark.unit
def test_load_video_preset_fast_default():
    """Test loading fast video preset with default values."""
    config = load_video_preset("fast")
    assert config.provider == "mock"
    assert config.model is None
    assert config.quality == "low"
    assert config.duration == 3.0


@pytest.mark.unit
def test_load_video_preset_regular_default():
    """Test loading regular video preset with default values."""
    config = load_video_preset("regular")
    assert config.provider == "veo"
    assert config.model == "veo-2.0-generate-001"
    assert config.quality == "standard"
    assert config.duration == 5.0


@pytest.mark.unit
def test_load_video_preset_ultra_default():
    """Test loading ultra video preset with default values."""
    config = load_video_preset("ultra")
    assert config.provider == "veo"
    assert config.model == "veo-2.0-generate-001"
    assert config.quality == "high"
    assert config.duration == 8.0


@pytest.mark.unit
def test_load_video_preset_env_override(monkeypatch):
    """Test that environment variables override video preset defaults."""
    monkeypatch.setenv("VIDEO_PRESET_FAST_PROVIDER", "veo")
    monkeypatch.setenv("VIDEO_PRESET_FAST_QUALITY", "medium")
    monkeypatch.setenv("VIDEO_PRESET_FAST_DURATION", "4.5")
    
    config = load_video_preset("fast")
    assert config.provider == "veo"
    assert config.quality == "medium"
    assert config.duration == 4.5


@pytest.mark.unit
def test_load_video_preset_invalid_duration_fallback(monkeypatch):
    """Test that invalid duration falls back to default."""
    monkeypatch.setenv("VIDEO_PRESET_FAST_DURATION", "invalid")
    
    config = load_video_preset("fast")
    assert config.duration == 3.0  # Falls back to default


@pytest.mark.unit
def test_get_default_model_for_provider():
    """Test getting default model for each provider."""
    assert get_default_model_for_provider("gemini") == "gemini-2.5-flash-image"
    assert get_default_model_for_provider("gemini-pro") == "gemini-3-pro-image-preview"
    assert get_default_model_for_provider("openai") == "gpt-image-1-mini"
    assert get_default_model_for_provider("google") == "imagen-3.0-generate-001"
    assert get_default_model_for_provider("unknown") == ""


@pytest.mark.unit
def test_image_preset_config_dataclass():
    """Test ImagePresetConfig dataclass creation."""
    config = ImagePresetConfig(
        provider="test-provider",
        model="test-model",
        size="1024x1024"
    )
    assert config.provider == "test-provider"
    assert config.model == "test-model"
    assert config.size == "1024x1024"


@pytest.mark.unit
def test_video_preset_config_dataclass():
    """Test VideoPresetConfig dataclass creation."""
    config = VideoPresetConfig(
        provider="test-provider",
        model="test-model",
        quality="high",
        duration=10.0
    )
    assert config.provider == "test-provider"
    assert config.model == "test-model"
    assert config.quality == "high"
    assert config.duration == 10.0

