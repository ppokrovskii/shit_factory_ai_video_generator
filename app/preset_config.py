"""Preset configuration loader for image and video generation.

This module provides preset-based configuration to simplify CLI usage.
Users can select quality presets (fast/regular/ultra) instead of manually
specifying providers, models, and parameters.

Environment variables:
    IMAGE_PRESET_{FAST|REGULAR|ULTRA}_{PROVIDER|MODEL|SIZE}
    VIDEO_PRESET_{FAST|REGULAR|ULTRA}_{PROVIDER|MODEL|QUALITY|DURATION}
"""
from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class ImagePresetConfig:
    """Configuration for image generation preset."""
    provider: str
    model: str
    size: str


@dataclass
class VideoPresetConfig:
    """Configuration for video generation preset."""
    provider: str
    model: Optional[str]
    quality: str
    duration: float


# Default configurations for image presets
_IMAGE_PRESET_DEFAULTS = {
    "fast": ImagePresetConfig(
        provider="openai",
        model="gpt-image-1-mini",
        size="1024x1024",
    ),
    "regular": ImagePresetConfig(
        provider="gemini",
        model="gemini-2.5-flash-image",
        size="1024x1024",
    ),
    "ultra": ImagePresetConfig(
        provider="gemini-pro",
        model="gemini-3-pro-image-preview",
        size="2048x2048",
    ),
}

# Default configurations for video presets
_VIDEO_PRESET_DEFAULTS = {
    "fast": VideoPresetConfig(
        provider="veo",
        model="veo-2.0-generate-001",
        quality="standard",
        duration=5.0,
    ),
    "regular": VideoPresetConfig(
        provider="veo",
        model="veo-2.0-generate-001",
        quality="high",
        duration=5.0,
    ),
    "ultra": VideoPresetConfig(
        provider="veo",
        model="veo-2.0-generate-001",
        quality="high",
        duration=10.0,
    ),
}


def load_image_preset(name: str) -> ImagePresetConfig:
    """Load image preset configuration from environment or defaults.
    
    Args:
        name: Preset name (fast, regular, or ultra)
    
    Returns:
        ImagePresetConfig with provider, model, and size
    
    Raises:
        ValueError: If preset name is not recognized
    
    Example:
        >>> config = load_image_preset("fast")
        >>> config.provider
        'openai'
    """
    name_lower = name.lower()
    if name_lower not in _IMAGE_PRESET_DEFAULTS:
        raise ValueError(
            f"Unknown image preset: {name}. "
            f"Valid options: {', '.join(_IMAGE_PRESET_DEFAULTS.keys())}"
        )
    
    default = _IMAGE_PRESET_DEFAULTS[name_lower]
    name_upper = name_lower.upper()
    
    # Load from environment with fallback to defaults
    provider = os.getenv(f"IMAGE_PRESET_{name_upper}_PROVIDER", default.provider)
    model = os.getenv(f"IMAGE_PRESET_{name_upper}_MODEL", default.model)
    size = os.getenv(f"IMAGE_PRESET_{name_upper}_SIZE", default.size)
    
    return ImagePresetConfig(provider=provider, model=model, size=size)


def load_video_preset(name: str) -> VideoPresetConfig:
    """Load video preset configuration from environment or defaults.
    
    Args:
        name: Preset name (fast, regular, or ultra)
    
    Returns:
        VideoPresetConfig with provider, model, quality, and duration
    
    Raises:
        ValueError: If preset name is not recognized
    
    Example:
        >>> config = load_video_preset("regular")
        >>> config.provider
        'veo'
    """
    name_lower = name.lower()
    if name_lower not in _VIDEO_PRESET_DEFAULTS:
        raise ValueError(
            f"Unknown video preset: {name}. "
            f"Valid options: {', '.join(_VIDEO_PRESET_DEFAULTS.keys())}"
        )
    
    default = _VIDEO_PRESET_DEFAULTS[name_lower]
    name_upper = name_lower.upper()
    
    # Load from environment with fallback to defaults
    provider = os.getenv(f"VIDEO_PRESET_{name_upper}_PROVIDER", default.provider)
    model = os.getenv(f"VIDEO_PRESET_{name_upper}_MODEL", default.model or "")
    quality = os.getenv(f"VIDEO_PRESET_{name_upper}_QUALITY", default.quality)
    duration_str = os.getenv(f"VIDEO_PRESET_{name_upper}_DURATION", str(default.duration))
    
    try:
        duration = float(duration_str)
    except ValueError:
        duration = default.duration
    
    return VideoPresetConfig(
        provider=provider,
        model=model if model else None,
        quality=quality,
        duration=duration,
    )


def get_default_model_for_provider(provider: str) -> str:
    """Get the default model name for a given provider.
    
    Args:
        provider: Provider name (gemini, gemini-pro, openai, google)
    
    Returns:
        Default model name for the provider
    """
    defaults = {
        "gemini": "gemini-2.5-flash-image",
        "gemini-pro": "gemini-3-pro-image-preview",
        "openai": "gpt-image-1-mini",
        "google": "imagen-3.0-generate-001",
    }
    return defaults.get(provider, "")

