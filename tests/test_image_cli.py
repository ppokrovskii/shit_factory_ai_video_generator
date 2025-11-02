"""Tests for the standalone image CLI (generate, refine, upscale)."""
from __future__ import annotations

import os
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import pytest
from typer.testing import CliRunner

from app.image_cli import app
from app.image_gen.base import ImageGenResult, ImagePrompt


@pytest.fixture
def runner():
    """Create CLI test runner."""
    return CliRunner()


@pytest.fixture
def temp_image(tmp_path):
    """Create a temporary test image."""
    from PIL import Image
    
    img_path = tmp_path / "test.png"
    img = Image.new("RGB", (100, 100), color="red")
    img.save(img_path)
    return img_path


@pytest.fixture
def mock_env(monkeypatch):
    """Set up mock environment variables."""
    monkeypatch.setenv("GOOGLE_API_KEY", "test-key")
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")


class TestGenerateCommand:
    """Tests for the 'generate' command."""
    
    def test_generate_basic(self, runner, tmp_path, mock_env):
        """Test basic image generation."""
        output = tmp_path / "output.png"
        
        # Mock the image provider
        with patch("app.image_cli._get_image_provider") as mock_provider:
            mock_instance = Mock()
            mock_provider.return_value = mock_instance
            
            # Create a real test image
            from PIL import Image
            img = Image.new("RGB", (100, 100), color="blue")
            img.save(output)
            
            mock_result = ImageGenResult(
                prompt=ImagePrompt(0, "gen", "test prompt"),
                path=output,
            )
            mock_instance.generate_images.return_value = [mock_result]
            
            result = runner.invoke(
                app,
                ["generate", "a test image", "--output", str(output)],
            )
            
            assert result.exit_code == 0
            assert "Image generated" in result.stdout
            mock_instance.generate_images.assert_called_once()
    
    def test_generate_with_negative_prompt(self, runner, tmp_path, mock_env):
        """Test generation with negative prompt."""
        output = tmp_path / "output.png"
        
        with patch("app.image_cli._get_image_provider") as mock_provider:
            mock_instance = Mock()
            mock_provider.return_value = mock_instance
            
            from PIL import Image
            img = Image.new("RGB", (100, 100), color="blue")
            img.save(output)
            
            mock_result = ImageGenResult(
                prompt=ImagePrompt(0, "gen", "test prompt", negative_prompt="blurry"),
                path=output,
            )
            mock_instance.generate_images.return_value = [mock_result]
            
            result = runner.invoke(
                app,
                [
                    "generate",
                    "a test image",
                    "--output", str(output),
                    "--negative", "blurry",
                ],
            )
            
            assert result.exit_code == 0
            # Check that negative prompt was passed
            call_args = mock_instance.generate_images.call_args
            prompt = call_args[0][0][0]
            assert prompt.negative_prompt == "blurry"
    
    def test_generate_with_seed(self, runner, tmp_path, mock_env):
        """Test generation with custom seed."""
        output = tmp_path / "output.png"
        
        with patch("app.image_cli._get_image_provider") as mock_provider:
            mock_instance = Mock()
            mock_provider.return_value = mock_instance
            
            from PIL import Image
            img = Image.new("RGB", (100, 100), color="blue")
            img.save(output)
            
            mock_result = ImageGenResult(
                prompt=ImagePrompt(0, "gen", "test prompt"),
                path=output,
            )
            mock_instance.generate_images.return_value = [mock_result]
            
            result = runner.invoke(
                app,
                ["generate", "a test image", "--output", str(output), "--seed", "42"],
            )
            
            assert result.exit_code == 0
            call_args = mock_instance.generate_images.call_args
            assert call_args[1]["seed"] == 42
    
    def test_generate_provider_selection(self, runner, tmp_path, mock_env):
        """Test different provider selections."""
        output = tmp_path / "output.png"
        providers = ["gemini", "openai", "google"]
        
        for provider in providers:
            with patch("app.image_cli._get_image_provider") as mock_provider:
                mock_instance = Mock()
                mock_provider.return_value = mock_instance
                
                from PIL import Image
                img = Image.new("RGB", (100, 100), color="blue")
                img.save(output)
                
                mock_result = ImageGenResult(
                    prompt=ImagePrompt(0, "gen", "test"),
                    path=output,
                )
                mock_instance.generate_images.return_value = [mock_result]
                
                result = runner.invoke(
                    app,
                    [
                        "generate",
                        "test",
                        "--output", str(output),
                        "--provider", provider,
                    ],
                )
                
                assert result.exit_code == 0
                mock_provider.assert_called_once_with(provider)


class TestRefineCommand:
    """Tests for the 'refine' command."""
    
    def test_refine_basic(self, runner, temp_image, tmp_path, mock_env):
        """Test basic image refinement."""
        output = tmp_path / "refined.png"
        
        with patch("app.image_cli._get_image_provider") as mock_provider:
            mock_instance = Mock()
            mock_provider.return_value = mock_instance
            
            from PIL import Image
            img = Image.new("RGB", (100, 100), color="green")
            img.save(output)
            
            mock_result = ImageGenResult(
                prompt=ImagePrompt(0, "refine", "make it better", attachment=temp_image.name),
                path=output,
            )
            mock_instance.generate_images.return_value = [mock_result]
            
            result = runner.invoke(
                app,
                ["refine", str(temp_image), "make it better", "--output", str(output)],
            )
            
            assert result.exit_code == 0
            assert "Image refined" in result.stdout
            
            # Check that attachment was set
            call_args = mock_instance.generate_images.call_args
            prompt = call_args[0][0][0]
            assert prompt.attachment == temp_image.name
    
    def test_refine_nonexistent_file(self, runner, tmp_path, mock_env):
        """Test refinement with nonexistent input file."""
        result = runner.invoke(
            app,
            ["refine", "nonexistent.png", "make it better"],
        )
        
        assert result.exit_code == 1
        # Check output (combines stdout + stderr)
        output_text = result.output if hasattr(result, 'output') else result.stdout
        assert "not found" in output_text.lower()
    
    def test_refine_stdin_not_implemented(self, runner, mock_env):
        """Test that stdin input shows not implemented message."""
        result = runner.invoke(
            app,
            ["refine", "-", "make it better"],
        )
        
        assert result.exit_code == 1
        output_text = result.output if hasattr(result, 'output') else result.stdout
        assert "not yet implemented" in output_text.lower()


class TestUpscaleCommand:
    """Tests for the 'upscale' command."""
    
    def test_upscale_basic(self, runner, temp_image, tmp_path):
        """Test basic image upscaling."""
        output = tmp_path / "upscaled.png"
        
        result = runner.invoke(
            app,
            ["upscale", str(temp_image), "--output", str(output), "--size", "200x200"],
        )
        
        assert result.exit_code == 0
        assert "Image upscaled" in result.stdout
        assert output.exists()
        
        # Check output size
        from PIL import Image
        img = Image.open(output)
        assert img.size == (200, 200)
    
    def test_upscale_large_size(self, runner, temp_image, tmp_path):
        """Test upscaling to large size (3000x3000)."""
        output = tmp_path / "upscaled.png"
        
        result = runner.invoke(
            app,
            ["upscale", str(temp_image), "--output", str(output), "--size", "3000x3000"],
        )
        
        assert result.exit_code == 0
        assert output.exists()
        
        from PIL import Image
        img = Image.open(output)
        assert img.size == (3000, 3000)
    
    def test_upscale_different_methods(self, runner, temp_image, tmp_path):
        """Test different upscaling methods."""
        methods = ["lanczos", "bicubic", "nearest", "bilinear"]
        
        for method in methods:
            output = tmp_path / f"upscaled_{method}.png"
            
            result = runner.invoke(
                app,
                [
                    "upscale",
                    str(temp_image),
                    "--output", str(output),
                    "--size", "200x200",
                    "--method", method,
                ],
            )
            
            assert result.exit_code == 0, f"Failed with method {method}: {result.stdout}"
            assert output.exists()
    
    def test_upscale_invalid_size_format(self, runner, temp_image, tmp_path):
        """Test upscaling with invalid size format."""
        result = runner.invoke(
            app,
            ["upscale", str(temp_image), "--size", "invalid"],
        )
        
        assert result.exit_code == 1
        output_text = result.output if hasattr(result, 'output') else result.stdout
        assert "invalid size format" in output_text.lower()
    
    def test_upscale_invalid_method(self, runner, temp_image, tmp_path):
        """Test upscaling with invalid method."""
        output = tmp_path / "upscaled.png"
        
        result = runner.invoke(
            app,
            [
                "upscale",
                str(temp_image),
                "--output", str(output),
                "--method", "invalid_method",
            ],
        )
        
        assert result.exit_code == 1
        output_text = result.output if hasattr(result, 'output') else result.stdout
        assert "unknown method" in output_text.lower()
    
    def test_upscale_nonexistent_file(self, runner, tmp_path):
        """Test upscaling with nonexistent input file."""
        result = runner.invoke(
            app,
            ["upscale", "nonexistent.png"],
        )
        
        assert result.exit_code == 1
        output_text = result.output if hasattr(result, 'output') else result.stdout
        assert "not found" in output_text.lower()


class TestHelperFunctions:
    """Tests for helper functions."""
    
    def test_get_image_provider_gemini(self):
        """Test getting Gemini provider."""
        from app.image_cli import _get_image_provider
        
        with patch("app.image_gen.gemini.GeminiImageProvider") as mock_class:
            mock_instance = Mock()
            mock_class.return_value = mock_instance
            
            provider = _get_image_provider("gemini")
            
            assert provider == mock_instance
            mock_class.assert_called_once()
    
    def test_get_image_provider_openai(self):
        """Test getting OpenAI provider."""
        from app.image_cli import _get_image_provider
        
        with patch("app.image_gen.openai.OpenAIImageProvider") as mock_class:
            mock_instance = Mock()
            mock_class.return_value = mock_instance
            
            provider = _get_image_provider("openai")
            
            assert provider == mock_instance
            mock_class.assert_called_once()
    
    def test_get_image_provider_google(self):
        """Test getting Google provider."""
        from app.image_cli import _get_image_provider
        
        with patch("app.image_gen.google.GoogleImageProvider") as mock_class:
            mock_instance = Mock()
            mock_class.return_value = mock_instance
            
            provider = _get_image_provider("google")
            
            assert provider == mock_instance
            mock_class.assert_called_once()
    
    def test_get_image_provider_invalid(self, runner):
        """Test getting invalid provider raises error."""
        from app.image_cli import _get_image_provider
        import typer
        
        with pytest.raises(typer.Exit):
            _get_image_provider("invalid_provider")
    
    def test_get_image_size(self, temp_image):
        """Test getting image size."""
        from app.image_cli import _get_image_size
        
        size_str = _get_image_size(temp_image)
        assert size_str == "100x100"
    
    def test_get_image_size_invalid_file(self, tmp_path):
        """Test getting size of invalid file."""
        from app.image_cli import _get_image_size
        
        invalid_file = tmp_path / "invalid.png"
        size_str = _get_image_size(invalid_file)
        assert size_str == "unknown"


class TestIntegration:
    """Integration tests for chaining operations."""
    
    def test_generate_then_upscale(self, runner, tmp_path, mock_env):
        """Test generating an image then upscaling it."""
        gen_output = tmp_path / "generated.png"
        upscale_output = tmp_path / "upscaled.png"
        
        # Generate
        with patch("app.image_cli._get_image_provider") as mock_provider:
            mock_instance = Mock()
            mock_provider.return_value = mock_instance
            
            from PIL import Image
            img = Image.new("RGB", (512, 512), color="blue")
            img.save(gen_output)
            
            mock_result = ImageGenResult(
                prompt=ImagePrompt(0, "gen", "test"),
                path=gen_output,
            )
            mock_instance.generate_images.return_value = [mock_result]
            
            result = runner.invoke(
                app,
                ["generate", "a test", "--output", str(gen_output)],
            )
            
            assert result.exit_code == 0
        
        # Upscale
        result = runner.invoke(
            app,
            ["upscale", str(gen_output), "--output", str(upscale_output), "--size", "1024x1024"],
        )
        
        assert result.exit_code == 0
        assert upscale_output.exists()
        
        from PIL import Image
        img = Image.open(upscale_output)
        assert img.size == (1024, 1024)
    
    def test_generate_refine_upscale(self, runner, tmp_path, mock_env):
        """Test full workflow: generate -> refine -> upscale."""
        gen_output = tmp_path / "generated.png"
        refined_output = tmp_path / "refined.png"
        upscale_output = tmp_path / "upscaled.png"
        
        # Generate
        with patch("app.image_cli._get_image_provider") as mock_provider:
            mock_instance = Mock()
            mock_provider.return_value = mock_instance
            
            from PIL import Image
            img = Image.new("RGB", (256, 256), color="red")
            img.save(gen_output)
            
            mock_result = ImageGenResult(
                prompt=ImagePrompt(0, "gen", "test"),
                path=gen_output,
            )
            mock_instance.generate_images.return_value = [mock_result]
            
            result = runner.invoke(
                app,
                ["generate", "a cat", "--output", str(gen_output)],
            )
            
            assert result.exit_code == 0
        
        # Refine
        with patch("app.image_cli._get_image_provider") as mock_provider:
            mock_instance = Mock()
            mock_provider.return_value = mock_instance
            
            from PIL import Image
            img = Image.new("RGB", (256, 256), color="green")
            img.save(refined_output)
            
            mock_result = ImageGenResult(
                prompt=ImagePrompt(0, "refine", "make fluffy", attachment=gen_output.name),
                path=refined_output,
            )
            mock_instance.generate_images.return_value = [mock_result]
            
            result = runner.invoke(
                app,
                ["refine", str(gen_output), "make fluffy", "--output", str(refined_output)],
            )
            
            assert result.exit_code == 0
        
        # Upscale
        result = runner.invoke(
            app,
            ["upscale", str(refined_output), "--output", str(upscale_output), "--size", "2048x2048"],
        )
        
        assert result.exit_code == 0
        assert upscale_output.exists()
        
        from PIL import Image
        img = Image.open(upscale_output)
        assert img.size == (2048, 2048)

