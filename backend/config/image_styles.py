"""
Конфигурация стилей изображений для генерации

Поддерживает 20 профессиональных стилей с рекомендациями по нишам
"""

IMAGE_STYLES = {
    "minimalist_stick_figure": {
        "name": "Minimalist Stick Figure",
        "prompt_suffix": "minimalist stick figure illustration, simple lines, clean background, educational style",
        "niches": ["psychology", "education", "business"],
        "emoji": "👤",
        "description": "Простые фигуры, чистый фон - отлично для психологии"
    },
    "anime": {
        "name": "Anime Style",
        "prompt_suffix": "anime style illustration, vibrant colors, expressive characters, manga aesthetic",
        "niches": ["entertainment", "storytelling", "gaming"],
        "emoji": "🎨",
        "description": "Яркий аниме стиль - подходит для историй и развлечений"
    },
    "watercolor": {
        "name": "Watercolor Painting",
        "prompt_suffix": "watercolor painting, soft brushstrokes, gentle colors, artistic, handmade aesthetic",
        "niches": ["lifestyle", "wellness", "meditation"],
        "emoji": "🖌️",
        "description": "Акварельная живопись - идеально для wellness контента"
    },
    "oil_painting": {
        "name": "Oil Painting",
        "prompt_suffix": "oil painting, classical art style, rich textures, museum quality",
        "niches": ["history", "art", "culture"],
        "emoji": "🖼️",
        "description": "Классическая живопись - для серьёзного контента"
    },
    "cyberpunk": {
        "name": "Cyberpunk",
        "prompt_suffix": "cyberpunk style, neon lights, futuristic cityscape, high-tech aesthetic",
        "niches": ["technology", "future", "sci-fi"],
        "emoji": "🌃",
        "description": "Неоновый киберпанк - для технологий и будущего"
    },
    "retro_80s": {
        "name": "Retro 80s",
        "prompt_suffix": "1980s retro style, vintage colors, synthwave aesthetic, nostalgic vibe",
        "niches": ["music", "entertainment", "nostalgia"],
        "emoji": "📼",
        "description": "Ретро 80-х - ностальгический контент"
    },
    "pixel_art": {
        "name": "Pixel Art",
        "prompt_suffix": "pixel art, 8-bit style, retro gaming aesthetic, sharp pixels",
        "niches": ["gaming", "tech", "retro"],
        "emoji": "🎮",
        "description": "Пиксельная графика - геймерский контент"
    },
    "comic_book": {
        "name": "Comic Book",
        "prompt_suffix": "comic book style, bold outlines, halftone dots, dynamic action",
        "niches": ["storytelling", "action", "entertainment"],
        "emoji": "💥",
        "description": "Комикс стиль - динамичные истории"
    },
    "photorealistic": {
        "name": "Photorealistic",
        "prompt_suffix": "photorealistic, ultra detailed, professional photography, 4K quality",
        "niches": ["documentary", "news", "professional"],
        "emoji": "📷",
        "description": "Фотореализм - серьёзный контент"
    },
    "clay_animation": {
        "name": "Clay Animation",
        "prompt_suffix": "claymation style, 3D clay figures, stop-motion aesthetic, playful",
        "niches": ["kids", "family", "education"],
        "emoji": "🧸",
        "description": "Пластилиновая анимация - детский контент"
    },
    "paper_cutout": {
        "name": "Paper Cut-out",
        "prompt_suffix": "paper cut-out style, layered paper, crafted aesthetic, shadows",
        "niches": ["crafts", "education", "storytelling"],
        "emoji": "✂️",
        "description": "Бумажная аппликация - творческий контент"
    },
    "neon_glow": {
        "name": "Neon Glow",
        "prompt_suffix": "neon glow effect, glowing lines, dark background, electric aesthetic",
        "niches": ["nightlife", "music", "modern"],
        "emoji": "✨",
        "description": "Неоновое свечение - ночная тематика"
    },
    "abstract_art": {
        "name": "Abstract Art",
        "prompt_suffix": "abstract art, geometric shapes, modern art, conceptual",
        "niches": ["art", "philosophy", "modern"],
        "emoji": "🎭",
        "description": "Абстракция - концептуальный контент"
    },
    "low_poly_3d": {
        "name": "Low Poly 3D",
        "prompt_suffix": "low poly 3D, geometric facets, modern 3D art, clean shapes",
        "niches": ["tech", "modern", "design"],
        "emoji": "🔷",
        "description": "Низкополигональная 3D графика - современный дизайн"
    },
    "sketch_drawing": {
        "name": "Sketch Drawing",
        "prompt_suffix": "pencil sketch, hand-drawn, artistic sketch lines, monochrome",
        "niches": ["art", "education", "casual"],
        "emoji": "✏️",
        "description": "Карандашный набросок - художественный стиль"
    },
    "digital_art": {
        "name": "Digital Art",
        "prompt_suffix": "digital art, professional illustration, smooth gradients, modern",
        "niches": ["general", "professional", "modern"],
        "emoji": "💻",
        "description": "Цифровое искусство - универсальный стиль"
    },
    "fantasy_art": {
        "name": "Fantasy Art",
        "prompt_suffix": "fantasy art, magical atmosphere, epic scene, detailed fantasy world",
        "niches": ["fantasy", "storytelling", "gaming"],
        "emoji": "🧙",
        "description": "Фэнтези - магические истории"
    },
    "scifi_concept": {
        "name": "Sci-Fi Concept",
        "prompt_suffix": "sci-fi concept art, futuristic technology, space age, sleek design",
        "niches": ["sci-fi", "technology", "future"],
        "emoji": "🚀",
        "description": "Научная фантастика - футуристический контент"
    },
    "vintage_poster": {
        "name": "Vintage Poster",
        "prompt_suffix": "vintage poster style, retro typography, aged paper, classic design",
        "niches": ["retro", "history", "classic"],
        "emoji": "📜",
        "description": "Винтажный постер - ретро контент"
    },
    "flat_design": {
        "name": "Flat Design",
        "prompt_suffix": "flat design, simple shapes, bold colors, minimalist modern",
        "niches": ["business", "infographic", "modern"],
        "emoji": "📊",
        "description": "Плоский дизайн - инфографика и бизнес"
    }
}


def get_style_prompt(style_key: str, base_prompt: str) -> str:
    """
    Получить полный промпт со стилем

    Args:
        style_key: Ключ стиля из IMAGE_STYLES
        base_prompt: Базовый промпт

    Returns:
        Полный промпт с добавленным стилем
    """
    if style_key not in IMAGE_STYLES:
        print(f"⚠️  Неизвестный стиль '{style_key}', использую minimalist_stick_figure")
        style_key = "minimalist_stick_figure"

    style = IMAGE_STYLES[style_key]
    return f"{base_prompt}, {style['prompt_suffix']}"


def get_recommended_styles(niche: str) -> list:
    """
    Получить рекомендованные стили для ниши

    Args:
        niche: Ниша контента (psychology, gaming, business и т.д.)

    Returns:
        Список рекомендованных стилей с метаданными
    """
    recommended = []
    for key, style in IMAGE_STYLES.items():
        if niche in style['niches']:
            recommended.append({
                'key': key,
                'name': style['name'],
                'emoji': style['emoji'],
                'description': style['description']
            })
    return recommended


def get_all_styles_for_ui() -> dict:
    """
    Получить все стили в формате для UI

    Returns:
        Словарь стилей с метаданными для отображения
    """
    ui_styles = {}
    for key, style in IMAGE_STYLES.items():
        ui_styles[key] = {
            'name': f"{style['emoji']} {style['name']}",
            'desc': style['description'],
            'niches': style['niches']
        }
    return ui_styles


def validate_style(style_key: str) -> bool:
    """
    Проверить, существует ли стиль

    Args:
        style_key: Ключ стиля для проверки

    Returns:
        True если стиль существует, иначе False
    """
    return style_key in IMAGE_STYLES
