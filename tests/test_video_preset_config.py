"""Unit tests for video preset configuration."""
import pytest
from app.preset_config import (
    load_video_preset,
    VideoPresetConfig,
)


@pytest.mark.unit
def test_load_video_preset_fast_default():
    """Test loading fast video preset with default values."""
    config = load_video_preset("fast")
    assert config.provider == "veo"
    assert config.model == "veo-2.0-generate-001"
    assert config.quality == "standard"
    assert config.duration == 5.0


@pytest.mark.unit
def test_load_video_preset_regular_default():
    """Test loading regular video preset with default values."""
    config = load_video_preset("regular")
    assert config.provider == "veo"
    assert config.model == "veo-2.0-generate-001"
    assert config.quality == "high"
    assert config.duration == 5.0


@pytest.mark.unit
def test_load_video_preset_ultra_default():
    """Test loading ultra video preset with default values."""
    config = load_video_preset("ultra")
    assert config.provider == "veo"
    assert config.quality == "high"
    assert config.duration == 10.0


@pytest.mark.unit
def test_load_video_preset_case_insensitive():
    """Test that preset names are case-insensitive."""
    config1 = load_video_preset("FAST")
    config2 = load_video_preset("Fast")
    config3 = load_video_preset("fast")
    
    assert config1.provider == config2.provider == config3.provider
    assert config1.quality == config2.quality == config3.quality


@pytest.mark.unit
def test_load_video_preset_invalid_name():
    """Test that invalid preset name raises ValueError."""
    with pytest.raises(ValueError, match="Unknown video preset"):
        load_video_preset("invalid")


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
def test_load_video_preset_partial_env_override(monkeypatch):
    """Test that env vars can override individual fields."""
    monkeypatch.setenv("VIDEO_PRESET_REGULAR_DURATION", "7.0")
    
    config = load_video_preset("regular")
    assert config.provider == "veo"  # Default
    assert config.quality == "high"  # Default
    assert config.duration == 7.0  # Overridden


@pytest.mark.unit
def test_load_video_preset_invalid_duration_fallback(monkeypatch):
    """Test that invalid duration falls back to default."""
    monkeypatch.setenv("VIDEO_PRESET_FAST_DURATION", "not-a-number")
    
    config = load_video_preset("fast")
    assert config.duration == 5.0  # Falls back to default


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

