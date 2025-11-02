from __future__ import annotations

import base64
import logging
import os
import subprocess
import shutil
import time
from pathlib import Path
from typing import Optional

import requests

from .base import Provider
from ..logging_conf import get_logger

logger = get_logger(__name__)


class VEOProvider:
    """Provider that uses Google Vertex AI Veo for video generation from first and last frames.

    Requires:
    - GOOGLE_CLOUD_PROJECT and ADC (Application Default Credentials)
    - VERTEX_VEO_OUTPUT_BUCKET (GCS bucket for temporary storage)
    
    Uses Vertex AI REST API to generate videos from image pairs.
    Reference: https://cloud.google.com/vertex-ai/generative-ai/docs/video/generate-videos-from-first-and-last-frames
    """

    def __init__(self, *, model: Optional[str] = None, fps: int = 24) -> None:
        self.model = model or os.getenv("VERTEX_VEO_MODEL", "veo-2.0-generate-001")
        self.fps_default = fps
        self.project = os.getenv("GOOGLE_CLOUD_PROJECT")
        self.location = os.getenv("VERTEX_LOCATION", "us-central1")
        
        if not self.project:
            raise RuntimeError(
                "GOOGLE_CLOUD_PROJECT not set in environment. "
                "This is required for Vertex AI Veo video generation."
            )
        
        # Cache gsutil command path
        self._gsutil_cmd = shutil.which("gsutil")

    def _get_access_token(self) -> str:
        """Get Google Cloud access token using gcloud CLI."""
        gcloud_cmd = shutil.which("gcloud")
        if not gcloud_cmd:
            raise RuntimeError(
                "gcloud CLI not found. Please install Google Cloud SDK: "
                "https://cloud.google.com/sdk/docs/install"
            )
        
        result = subprocess.run(
            [gcloud_cmd, "auth", "print-access-token"],
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout.strip()

    def _get_gcs_video_uri(self, out_path: Path) -> tuple[str, str]:
        """
        Generate deterministic GCS URI for video.
        
        Returns:
            tuple: (gcs_bucket_uri, gcs_video_uri)
        """
        gcs_bucket = os.getenv("VERTEX_VEO_OUTPUT_BUCKET")
        if not gcs_bucket:
            raise RuntimeError(
                "VERTEX_VEO_OUTPUT_BUCKET not set in environment. "
                "Veo requires a GCS bucket URI to store generated videos. "
                "Example: gs://your-bucket-name/videos/"
            )
        
        if not gcs_bucket.endswith("/"):
            gcs_bucket += "/"
        
        # Deterministic filename: <output_name>_<model>
        # NOTE: Vertex AI treats the storageUri as a directory prefix and creates
        # a subdirectory structure, so we should NOT include the .mp4 extension here
        model_slug = self.model.replace(".", "_").replace("-", "_")
        filename_prefix = f"{out_path.stem}_{model_slug}"
        
        return gcs_bucket, f"{gcs_bucket}{filename_prefix}"

    def _check_gcs_exists(self, gcs_uri: str) -> bool:
        """Check if video already exists in GCS."""
        if not self._gsutil_cmd:
            return False
        
        try:
            result = subprocess.run(
                [self._gsutil_cmd, "stat", gcs_uri],
                capture_output=True,
                text=True,
                timeout=10,
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, Exception) as e:
            logger.warning("GCS stat check failed: %s", e)
            return False

    def _download_from_gcs(self, gcs_uri: str, local_path: Path) -> None:
        """Download video from GCS to local path.
        
        Vertex AI creates a directory structure in GCS, so the gcs_uri will be a prefix
        and the actual video will be inside a subdirectory. We download to a temp directory,
        then find and move the video file to the final location.
        """
        if not self._gsutil_cmd:
            raise RuntimeError(
                "gsutil not found in PATH. Please ensure Google Cloud SDK is installed."
            )
        
        local_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Vertex AI stores videos in a directory structure: gs://bucket/prefix/.../*.mp4
        # Use wildcard to find the actual video file
        wildcard_uri = gcs_uri.rstrip('/') + '/**/*.mp4'
        
        # Create temp subdirectory for download
        temp_dir = local_path.parent / f".tmp_{local_path.stem}"
        temp_dir.mkdir(parents=True, exist_ok=True)
        
        try:
            # Use gsutil cp with recursive wildcard to download to temp directory
            result = subprocess.run(
                [self._gsutil_cmd, "-m", "cp", "-r", wildcard_uri, str(temp_dir)],
                capture_output=True,
                text=True,
                timeout=60,
            )
            
            if result.returncode != 0:
                raise RuntimeError(
                    f"Failed to download video from GCS. URI: {gcs_uri}, "
                    f"Wildcard: {wildcard_uri}. Error: {result.stderr}"
                )
            
            # Find the downloaded .mp4 file in temp directory
            mp4_files = list(temp_dir.rglob("*.mp4"))
            if not mp4_files:
                raise RuntimeError(
                    f"No .mp4 file found in downloaded content from {gcs_uri}"
                )
            
            if len(mp4_files) > 1:
                logger.warning(
                    "Multiple .mp4 files found, using first: %s",
                    [f.name for f in mp4_files]
                )
            
            # Move the video file to final location
            mp4_files[0].rename(local_path)
        finally:
            # Clean up temp directory
            if temp_dir.exists():
                shutil.rmtree(temp_dir, ignore_errors=True)

    def _delete_from_gcs(self, gcs_uri: str, target_name: str) -> None:
        """Delete video from GCS after successful download (auto-cleanup)."""
        if not self._gsutil_cmd:
            return
        
        try:
            # Use -r flag to recursively delete directory structure that Veo creates
            result = subprocess.run(
                [self._gsutil_cmd, "-m", "rm", "-r", gcs_uri],
                capture_output=True,
                text=True,
                timeout=10,
            )
            if result.returncode == 0:
                logger.info(
                    "vid-gen cleanup | target=%s deleted_from_gcs=%s",
                    target_name,
                    gcs_uri,
                )
            else:
                logger.warning(
                    "vid-gen cleanup | target=%s failed: %s",
                    target_name,
                    result.stderr,
                )
        except Exception as e:
            logger.warning(
                "vid-gen cleanup | target=%s error: %s",
                target_name,
                e,
            )

    def _reuse_existing_video(self, gcs_uri: str, out_path: Path) -> bool:
        """
        Try to reuse existing video from GCS (from interrupted run).
        
        Returns:
            bool: True if video was reused successfully
        """
        if not self._check_gcs_exists(gcs_uri):
            return False
        
        logger.info(
            "vid-gen reuse | target=%s found_in_gcs=%s (skipping generation)",
            out_path.name,
            gcs_uri,
        )
        
        try:
            self._download_from_gcs(gcs_uri, out_path)
            file_size_mb = out_path.stat().st_size / (1024 * 1024)
            logger.info(
                "vid-gen done  | target=%s size=%.2fMB reused_from_gcs=%s",
                out_path.name,
                file_size_mb,
                gcs_uri,
            )
            self._delete_from_gcs(gcs_uri, out_path.name)
            return True
        except Exception as e:
            logger.warning(
                "vid-gen reuse failed | target=%s error=%s, will regenerate",
                out_path.name,
                e,
            )
            return False

    def _encode_image(self, image_path: Path) -> tuple[str, str]:
        """
        Encode image to base64.
        
        Returns:
            tuple: (base64_string, mime_type)
        """
        img_data = image_path.read_bytes()
        b64_data = base64.b64encode(img_data).decode('utf-8')
        
        ext = image_path.suffix.lower()
        mime_map = {
            '.png': 'image/png',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.webp': 'image/webp',
        }
        mime_type = mime_map.get(ext, 'image/png')
        
        return b64_data, mime_type

    def _submit_generation_request(
        self,
        start_path: Path,
        end_path: Path,
        gcs_video_uri: str,
        access_token: str,
        video_prompt: str | None = None,
    ) -> str:
        """
        Submit video generation request to Vertex AI.
        
        Args:
            video_prompt: Optional specific prompt for this transition. If None, uses default.
        
        Returns:
            str: Operation name for polling
        """
        start_b64, start_mime = self._encode_image(start_path)
        end_b64, end_mime = self._encode_image(end_path)
        
        # Use custom prompt if provided, otherwise use generic default
        if video_prompt:
            prompt = video_prompt
        else:
            prompt = (
                "Create a smooth cinematic transition from the first frame to the last frame. "
                "The transition should be natural, maintaining visual continuity and quality. "
                "Apply smooth morphing and blending between the scenes."
            )
        
        url = (
            f"https://{self.location}-aiplatform.googleapis.com/v1/"
            f"projects/{self.project}/locations/{self.location}/"
            f"publishers/google/models/{self.model}:predictLongRunning"
        )
        
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json; charset=utf-8",
        }
        
        body = {
            "instances": [{
                "prompt": prompt,
                "image": {
                    "bytesBase64Encoded": start_b64,
                    "mimeType": start_mime,
                },
                "lastFrame": {
                    "bytesBase64Encoded": end_b64,
                    "mimeType": end_mime,
                },
            }],
            "parameters": {
                "storageUri": gcs_video_uri,
                "sampleCount": 1,
                "generateAudio": False,
            },
        }
        
        response = requests.post(url, headers=headers, json=body, timeout=60)
        response.raise_for_status()
        result = response.json()
        
        operation_name = result.get("name")
        if not operation_name:
            raise RuntimeError(f"No operation name in response: {result}")
        
        return operation_name

    def _poll_for_completion(
        self,
        operation_name: str,
        target_name: str,
        access_token: str,
        max_polls: int = 180,
    ) -> None:
        """
        Poll operation until video generation completes.
        
        Args:
            operation_name: Full operation name from initial request
            target_name: Target filename for logging
            access_token: GCP access token
            max_polls: Maximum number of 20s polls (default: 180 = 60 min)
        """
        poll_url = (
            f"https://{self.location}-aiplatform.googleapis.com/v1/"
            f"projects/{self.project}/locations/{self.location}/"
            f"publishers/google/models/{self.model}:fetchPredictOperation"
        )
        
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json; charset=utf-8",
        }
        
        poll_body = {"operationName": operation_name}
        operation_id = operation_name.split("/")[-1]
        
        logger.info(
            "vid-gen poll  | target=%s operation_id=%s (polling every 20s, timeout 60min)",
            target_name,
            operation_id,
        )
        
        poll_count = 0
        while poll_count < max_polls:
            time.sleep(20)
            poll_count += 1
            
            response = requests.post(
                poll_url,
                headers=headers,
                json=poll_body,
                timeout=60,
            )
            response.raise_for_status()
            operation = response.json()
            
            if operation.get("done"):
                if "error" in operation:
                    error_msg = operation["error"]
                    logger.error(
                        "vid-gen failed | target=%s error=%s",
                        target_name,
                        error_msg,
                    )
                    raise RuntimeError(f"Video generation failed: {error_msg}")
                return
            
            # Log progress every 5 polls (every 100 seconds)
            if poll_count % 5 == 0:
                elapsed_min = (poll_count * 20) / 60
                logger.info(
                    "vid-gen poll  | target=%s status=in_progress elapsed=%.1fmin polls=%d",
                    target_name,
                    elapsed_min,
                    poll_count,
                )
        
        # Timeout
        logger.error(
            "vid-gen timeout | target=%s elapsed=%dmin",
            target_name,
            (max_polls * 20) // 60,
        )
        raise RuntimeError(f"Video generation timed out after {max_polls * 20} seconds")

    def generate_transition(
        self,
        start_path: Path,
        end_path: Path,
        duration_s: float,
        out_path: Path,
        *,
        fps: int = 24,
        video_prompt: str | None = None,
    ) -> None:
        """
        Generate transition video between two images using Vertex AI Veo.
        
        Args:
            start_path: Path to start frame image
            end_path: Path to end frame image
            duration_s: Video duration in seconds (passed to API, may not be exact)
            out_path: Where to save the generated video
            fps: Frames per second (default: 24)
            video_prompt: Optional specific prompt for this transition
        """
        # Skip if already exists locally
        if out_path.exists():
            logger.info(
                "vid-gen skip  | target=%s (already exists)",
                out_path.name,
            )
            return
        
        logger.info(
            "vid-gen start | target=%s start=%s end=%s duration=%.1fs",
            out_path.name,
            start_path.name,
            end_path.name,
            duration_s,
        )
        
        try:
            # Get GCS URI for this video
            gcs_bucket, gcs_video_uri = self._get_gcs_video_uri(out_path)
            
            # Try to reuse existing video from GCS (from interrupted run)
            if self._reuse_existing_video(gcs_video_uri, out_path):
                return
            
            # Get access token
            access_token = self._get_access_token()
            
            # Submit generation request
            logger.info(
                "vid-gen submit | target=%s model=%s prompt=%s",
                out_path.name,
                self.model,
                "custom" if video_prompt else "default",
            )
            operation_name = self._submit_generation_request(
                start_path,
                end_path,
                gcs_video_uri,
                access_token,
                video_prompt,
            )
            
            # Poll until completion
            self._poll_for_completion(
                operation_name,
                out_path.name,
                access_token,
            )
            
            # Download generated video
            logger.info(
                "vid-gen download | target=%s gcs_uri=%s",
                out_path.name,
                gcs_video_uri,
            )
            self._download_from_gcs(gcs_video_uri, out_path)
            
            # Log completion
            file_size_mb = out_path.stat().st_size / (1024 * 1024)
            logger.info(
                "vid-gen done  | target=%s size=%.2fMB wrote=%s",
                out_path.name,
                file_size_mb,
                str(out_path),
            )
            
            # Auto-cleanup: delete from GCS to save storage costs
            self._delete_from_gcs(gcs_video_uri, out_path.name)
            
        except Exception as exc:
            logger.error(
                "vid-gen error | target=%s error=%s",
                out_path.name,
                str(exc),
            )
            raise
