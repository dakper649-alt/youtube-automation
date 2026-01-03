"""Configuration module for YouTube automation system"""

from .image_styles import (
    IMAGE_STYLES,
    get_style_prompt,
    get_recommended_styles,
    get_all_styles_for_ui,
    validate_style
)

__all__ = [
    'IMAGE_STYLES',
    'get_style_prompt',
    'get_recommended_styles',
    'get_all_styles_for_ui',
    'validate_style'
]
