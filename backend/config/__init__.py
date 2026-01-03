"""Configuration module for YouTube automation system"""

from .image_styles import (
    IMAGE_STYLES,
    get_style_prompt,
    get_recommended_styles,
    get_all_styles_for_ui,
    validate_style
)

from .voices import (
    ELEVENLABS_VOICES,
    get_recommended_voices,
    get_voice_id,
    get_preview_text,
    get_all_voices_for_ui as get_all_voices,
    validate_voice,
    get_voices_by_category
)

from .background_music import (
    BACKGROUND_MUSIC,
    get_recommended_music,
    get_music_volume,
    get_music_path,
    validate_music,
    get_all_music_for_ui,
    get_music_by_category
)

__all__ = [
    # Image styles
    'IMAGE_STYLES',
    'get_style_prompt',
    'get_recommended_styles',
    'get_all_styles_for_ui',
    'validate_style',
    # Voices
    'ELEVENLABS_VOICES',
    'get_recommended_voices',
    'get_voice_id',
    'get_preview_text',
    'get_all_voices',
    'validate_voice',
    'get_voices_by_category',
    # Background music
    'BACKGROUND_MUSIC',
    'get_recommended_music',
    'get_music_volume',
    'get_music_path',
    'validate_music',
    'get_all_music_for_ui',
    'get_music_by_category'
]
