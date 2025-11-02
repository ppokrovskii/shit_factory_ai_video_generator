from dataclasses import dataclass
from pathlib import Path
from typing import List, Tuple


@dataclass
class VideoPair:
    """Represents a video transition pair with optional prompt."""
    start_image: Path
    end_image: Path
    video_prompt: str | None = None


def consecutive_pairs(items: List[Path]) -> List[Tuple[Path, Path]]:
    """Legacy function returning tuples for backward compatibility."""
    if len(items) < 2:
        return []
    return [(items[i], items[i + 1]) for i in range(len(items) - 1)]


def consecutive_video_pairs(items: List[Path], prompts: dict[str, str] | None = None) -> List[VideoPair]:
    """
    Create VideoPair objects from consecutive items with optional video prompts.
    
    DEPRECATED: This creates pairs from all consecutive images, which may not match
    the intended video transitions. Use video_pairs_from_prompts() when prompts are available.
    
    Args:
        items: List of image paths
        prompts: Optional dict mapping transition names to video prompts
                 e.g., {"S01_to_S02": "prompt text"}
    
    Returns:
        List of VideoPair objects
    """
    if len(items) < 2:
        return []
    
    pairs = []
    for i in range(len(items) - 1):
        start = items[i]
        end = items[i + 1]
        
        # Try to find matching video prompt
        video_prompt = None
        if prompts:
            # Try various naming patterns
            start_code = start.stem.split('_')[0]  # e.g., "S01" from "S01_girl_01A"
            end_code = end.stem.split('_')[0]      # e.g., "S02" from "S02_girl_01B"
            transition_key = f"{start_code}_to_{end_code}"
            video_prompt = prompts.get(transition_key)
        
        pairs.append(VideoPair(start_image=start, end_image=end, video_prompt=video_prompt))
    
    return pairs


def video_pairs_from_prompts(
    available_images: List[Path],
    prompts_dict: dict[str, str]
) -> List[VideoPair]:
    """
    Create VideoPair objects based on video_prompts dictionary keys.
    Only creates pairs that are explicitly defined in the prompts.
    
    Args:
        available_images: List of available image paths
        prompts_dict: Dict mapping transition names to video prompts
                      e.g., {"S01_to_S02": "prompt text"}
    
    Returns:
        List of VideoPair objects for explicitly defined transitions
    """
    if not prompts_dict:
        return []
    
    # Build a map of image codes to paths for quick lookup
    image_map = {}
    for img in available_images:
        code = img.stem.split('_')[0]  # e.g., "S01" from "S01_girl_01A"
        image_map[code] = img
    
    pairs = []
    for transition_key, prompt in prompts_dict.items():
        # Parse transition key like "S01_to_S02"
        parts = transition_key.split('_to_')
        if len(parts) != 2:
            continue
        
        start_code, end_code = parts
        
        # Find matching images
        start_img = image_map.get(start_code)
        end_img = image_map.get(end_code)
        
        if start_img and end_img:
            pairs.append(VideoPair(
                start_image=start_img,
                end_image=end_img,
                video_prompt=prompt
            ))
    
    return pairs


