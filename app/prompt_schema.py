from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import List

from .image_gen.base import ImagePrompt


@dataclass(frozen=True)
class PromptFile:
    clips: List[ImagePrompt]
    video_prompts: dict[str, str]  # Maps "S01_to_S02" to video prompt text


def _coerce_negative_prompt(value: object) -> str | None:
    if value is None:
        return None
    if isinstance(value, str):
        return value
    if isinstance(value, list):
        if all(isinstance(x, str) for x in value):
            return ", ".join(value)
    raise ValueError("negative_prompt must be a string or list of strings")


def load_prompts(path: Path) -> PromptFile:
    if path.suffix.lower() != ".json":
        raise ValueError("Prompts must be provided as a .json file")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON: {exc}") from exc

    if not isinstance(data, dict):
        raise ValueError("Invalid schema: expected object")
    
    # Support new schema (images/videos arrays) and old schema (clips array)
    if "images" in data and "videos" in data:
        return _load_new_schema(data)
    elif "clips" in data:
        return _load_old_schema(data)
    else:
        raise ValueError("Invalid schema: expected 'images'+'videos' arrays or 'clips' array")


def _load_new_schema(data: dict) -> PromptFile:
    """Load schema v2.0 with separate images and videos arrays."""
    if not isinstance(data["images"], list):
        raise ValueError("Invalid schema: 'images' must be an array")
    if not isinstance(data["videos"], list):
        raise ValueError("Invalid schema: 'videos' must be an array")
    
    # First pass: create filename->index map and build dependency chains
    filename_to_idx = {}
    images_data = []
    
    for idx, img in enumerate(data["images"]):
        if not isinstance(img, dict):
            raise ValueError(f"Invalid schema: image {idx} must be an object")
        
        code = img.get("code")
        filename = img.get("filename")
        prompt = img.get("prompt")
        reference = img.get("reference")
        
        if not isinstance(code, str) or not code:
            raise ValueError(f"Invalid schema: image {idx}.code must be non-empty string")
        if not isinstance(filename, str) or not filename:
            raise ValueError(f"Invalid schema: image {idx}.filename must be non-empty string")
        if not isinstance(prompt, str) or not prompt:
            raise ValueError(f"Invalid schema: image {idx}.prompt must be non-empty string")
        if reference is not None and not isinstance(reference, str):
            raise ValueError(f"Invalid schema: image {idx}.reference must be filename string or null")
        
        filename_to_idx[filename] = idx
        images_data.append((idx, code, filename, prompt, reference))
    
    # Second pass: assign groups based on dependency chains
    # Images with same "root" (first in chain) get same group to ensure sequential processing
    prompts: List[ImagePrompt] = []
    
    for idx, code, filename, prompt, reference in images_data:
        # Find the root of the dependency chain
        current_ref = reference
        root_idx = idx
        while current_ref is not None and current_ref in filename_to_idx:
            root_idx = filename_to_idx[current_ref]
            # Look up reference of root to continue chain
            for _, _, fn, _, ref in images_data:
                if fn == current_ref:
                    current_ref = ref
                    break
            else:
                break
        
        # Use root index as group to keep dependent images together
        group_id = f"chain_{root_idx}"
        
        prompts.append(
            ImagePrompt(
                index=idx,
                code=code,
                positive_prompt=prompt,
                negative_prompt=None,  # Not used in new schema
                target_filename=filename,
                attachment=reference,  # Reference is now directly a filename
                group=group_id,  # Group by dependency chain
            )
        )
    
    # Build video_prompts map from videos array
    # Create code lookup for building transition keys
    filename_to_code = {img["filename"]: img["code"] for img in data["images"]}
    
    video_prompts_map: dict[str, str] = {}
    for video in data["videos"]:
        if not isinstance(video, dict):
            raise ValueError("Invalid schema: video must be an object")
        
        from_file = video.get("from")
        to_file = video.get("to")
        video_prompt = video.get("prompt")
        
        if not isinstance(from_file, str) or not from_file:
            raise ValueError("Invalid schema: video.from must be non-empty string")
        if not isinstance(to_file, str) or not to_file:
            raise ValueError("Invalid schema: video.to must be non-empty string")
        if not isinstance(video_prompt, str) or not video_prompt:
            raise ValueError("Invalid schema: video.prompt must be non-empty string")
        
        # Convert filenames to codes for transition key (for backward compatibility with CLI)
        from_code = filename_to_code.get(from_file, from_file.split('_')[0] if '_' in from_file else from_file)
        to_code = filename_to_code.get(to_file, to_file.split('_')[0] if '_' in to_file else to_file)
        
        transition_key = f"{from_code}_to_{to_code}"
        video_prompts_map[transition_key] = video_prompt
    
    return PromptFile(clips=prompts, video_prompts=video_prompts_map)


def _load_old_schema(data: dict) -> PromptFile:
    """Load old schema with clips array (backward compatibility)."""
    if not isinstance(data["clips"], list):
        raise ValueError("Invalid schema: expected 'clips' array")

    prompts: List[ImagePrompt] = []
    video_prompts_map: dict[str, str] = {}
    
    for idx, clip in enumerate(data["clips"]):
        if not isinstance(clip, dict):
            raise ValueError("Invalid schema: each clip must be an object")
        code = clip.get("code")
        
        # Support both old (positive_prompt) and new (image_prompt) field names
        pos = clip.get("image_prompt") or clip.get("positive_prompt")
        
        neg = clip.get("negative_prompt")
        target_filename = clip.get("target_filename")
        attachment = clip.get("attachment")
        group = clip.get("group")
        video_prompt = clip.get("video_prompt")
        
        if not isinstance(code, str) or not code:
            raise ValueError("Invalid schema: clip.code must be non-empty string")
        if not isinstance(pos, str) or not pos:
            raise ValueError("Invalid schema: clip.image_prompt/positive_prompt must be non-empty string")
        negs = _coerce_negative_prompt(neg)
        if target_filename is not None and not isinstance(target_filename, str):
            raise ValueError("Invalid schema: clip.target_filename must be string if present")
        if attachment is not None and not isinstance(attachment, str):
            raise ValueError("Invalid schema: clip.attachment must be string if present")
        if group is not None and not isinstance(group, str):
            raise ValueError("Invalid schema: clip.group must be string if present")
        if video_prompt is not None and not isinstance(video_prompt, str):
            raise ValueError("Invalid schema: clip.video_prompt must be string if present")
        
        prompts.append(
            ImagePrompt(
                index=idx,
                code=code,
                positive_prompt=pos,
                negative_prompt=negs,
                target_filename=target_filename,
                attachment=attachment,
                group=group,
            )
        )
        
        # Build video_prompts map for transitions (B clips typically)
        if video_prompt and idx > 0:
            prev_code = data["clips"][idx - 1].get("code")
            if prev_code:
                transition_key = f"{prev_code}_to_{code}"
                video_prompts_map[transition_key] = video_prompt

    return PromptFile(clips=prompts, video_prompts=video_prompts_map)


