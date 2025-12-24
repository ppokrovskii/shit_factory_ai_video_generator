"""Integration tests for image-cli with Gemini Pro provider."""
import subprocess
import sys
from pathlib import Path
import pytest


@pytest.mark.integration
def test_video_cli_with_gemini_pro_image_provider(tmp_path):
    """Test video-cli with gemini-pro image provider."""
    src_dir = tmp_path / "src"
    src_dir.mkdir()
    
    # Create dummy images
    from PIL import Image
    for i in range(2):
        img = Image.new('RGB', (100, 100), color='red')
        img.save(src_dir / f"img{i}.png")
    
    out_dir = tmp_path / "out"
    
    result = subprocess.run(
        [
            sys.executable, "-m", "app.cli",
            "--src", str(src_dir),
            "--out", str(out_dir),
            "--img-provider", "gemini-pro",
            "--provider", "mock",
            "--dry-run",
        ],
        capture_output=True,
        text=True,
    )
    
    # Should complete dry-run successfully
    assert result.returncode == 0


