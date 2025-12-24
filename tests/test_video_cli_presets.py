"""Integration tests for video-cli with preset support."""
import subprocess
import sys
from pathlib import Path
import pytest


@pytest.mark.integration
def test_video_cli_with_fast_preset(tmp_path):
    """Test video-cli with fast preset."""
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
            "--video-preset", "fast",
            "--dry-run",
        ],
        capture_output=True,
        text=True,
    )
    
    # Should complete dry-run successfully
    assert result.returncode == 0


@pytest.mark.integration
def test_video_cli_backward_compat_with_old_provider_flag(tmp_path):
    """Test backward compatibility with old --provider veo syntax."""
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
            "--provider", "mock",
            "--dry-run",
        ],
        capture_output=True,
        text=True,
    )
    
    # Should still work (backward compatibility)
    assert result.returncode == 0


