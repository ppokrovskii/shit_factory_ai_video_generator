"""Integration tests for image-cli with preset support."""
import subprocess
import sys
from pathlib import Path
import pytest


@pytest.mark.integration
def test_image_cli_help_shows_presets():
    """Test that help text mentions presets."""
    result = subprocess.run(
        [sys.executable, "-m", "app.image_cli", "generate", "--help"],
        capture_output=True,
        text=True,
    )
    
    assert result.returncode == 0
    # Help should mention preset options
    assert "fast" in result.stdout.lower() or "preset" in result.stdout.lower()


