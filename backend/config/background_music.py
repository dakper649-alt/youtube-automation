"""
Конфигурация фоновой музыки из YouTube Audio Library
Все треки бесплатны и не требуют атрибуции
"""

import os

BACKGROUND_MUSIC = {
    # ═══════════════════════════════════════════════════════════════
    # ПСИХОЛОГИЯ / МЕДИТАЦИЯ / WELLNESS
    # ═══════════════════════════════════════════════════════════════
    "calm_piano": {
        "name": "Calm Piano",
        "filename": "calm_piano.mp3",
        "url": "https://www.youtube.com/audiolibrary/music",
        "genre": "ambient",
        "mood": "calm",
        "niches": ["psychology", "meditation", "wellness", "self-help"],
        "emoji": "🎹",
        "description": "Спокойное фортепиано - идеально для психологии",
        "volume": -20,  # dB (тише голоса)
        "recommended": True
    },
    "soft_strings": {
        "name": "Soft Strings",
        "filename": "soft_strings.mp3",
        "url": "https://www.youtube.com/audiolibrary/music",
        "genre": "ambient",
        "mood": "peaceful",
        "niches": ["meditation", "wellness", "spirituality"],
        "emoji": "🎻",
        "description": "Мягкие струнные - для медитации",
        "volume": -22
    },
    "ambient_nature": {
        "name": "Ambient Nature",
        "filename": "ambient_nature.mp3",
        "url": "https://www.youtube.com/audiolibrary/music",
        "genre": "ambient",
        "mood": "relaxing",
        "niches": ["wellness", "nature", "relaxation"],
        "emoji": "🌿",
        "description": "Звуки природы - расслабление",
        "volume": -18
    },

    # ═══════════════════════════════════════════════════════════════
    # БИЗНЕС / МОТИВАЦИЯ / КОРПОРАТИВНОЕ
    # ═══════════════════════════════════════════════════════════════
    "uplifting_corporate": {
        "name": "Uplifting Corporate",
        "filename": "uplifting_corporate.mp3",
        "url": "https://www.youtube.com/audiolibrary/music",
        "genre": "corporate",
        "mood": "uplifting",
        "niches": ["business", "entrepreneurship", "marketing"],
        "emoji": "💼",
        "description": "Мотивирующая корпоративная музыка",
        "volume": -20,
        "recommended": True
    },
    "inspiring_orchestral": {
        "name": "Inspiring Orchestral",
        "filename": "inspiring_orchestral.mp3",
        "url": "https://www.youtube.com/audiolibrary/music",
        "genre": "orchestral",
        "mood": "inspiring",
        "niches": ["motivation", "success", "achievement"],
        "emoji": "🎺",
        "description": "Вдохновляющий оркестр - достижения",
        "volume": -18
    },
    "modern_tech": {
        "name": "Modern Tech",
        "filename": "modern_tech.mp3",
        "url": "https://www.youtube.com/audiolibrary/music",
        "genre": "electronic",
        "mood": "focused",
        "niches": ["technology", "innovation", "startup"],
        "emoji": "💻",
        "description": "Современная электроника - технологии",
        "volume": -20
    },

    # ═══════════════════════════════════════════════════════════════
    # ИСТОРИИ / ДРАМА / MYSTERY
    # ═══════════════════════════════════════════════════════════════
    "cinematic_tension": {
        "name": "Cinematic Tension",
        "filename": "cinematic_tension.mp3",
        "url": "https://www.youtube.com/audiolibrary/music",
        "genre": "cinematic",
        "mood": "tense",
        "niches": ["storytelling", "thriller", "mystery"],
        "emoji": "🎬",
        "description": "Кинематографическое напряжение - триллеры",
        "volume": -18,
        "recommended": True
    },
    "emotional_piano": {
        "name": "Emotional Piano",
        "filename": "emotional_piano.mp3",
        "url": "https://www.youtube.com/audiolibrary/music",
        "genre": "cinematic",
        "mood": "emotional",
        "niches": ["drama", "emotional", "storytelling"],
        "emoji": "😢",
        "description": "Эмоциональное фортепиано - драма",
        "volume": -20
    },
    "suspense_strings": {
        "name": "Suspense Strings",
        "filename": "suspense_strings.mp3",
        "url": "https://www.youtube.com/audiolibrary/music",
        "genre": "cinematic",
        "mood": "suspense",
        "niches": ["mystery", "investigation", "true_crime"],
        "emoji": "🔍",
        "description": "Саспенс - детективы и расследования",
        "volume": -18
    },

    # ═══════════════════════════════════════════════════════════════
    # ОБРАЗОВАНИЕ / TUTORIAL / NEUTRAL
    # ═══════════════════════════════════════════════════════════════
    "light_background": {
        "name": "Light Background",
        "filename": "light_background.mp3",
        "url": "https://www.youtube.com/audiolibrary/music",
        "genre": "acoustic",
        "mood": "neutral",
        "niches": ["education", "tutorial", "how-to"],
        "emoji": "📚",
        "description": "Лёгкий фон - обучающие видео",
        "volume": -22,
        "recommended": True
    },
    "neutral_corporate": {
        "name": "Neutral Corporate",
        "filename": "neutral_corporate.mp3",
        "url": "https://www.youtube.com/audiolibrary/music",
        "genre": "corporate",
        "mood": "neutral",
        "niches": ["professional", "presentation", "informative"],
        "emoji": "📊",
        "description": "Нейтральная корпоративная - презентации",
        "volume": -22
    },

    # ═══════════════════════════════════════════════════════════════
    # ЭНЕРГИЧНОЕ / UPBEAT / FUN
    # ═══════════════════════════════════════════════════════════════
    "upbeat_acoustic": {
        "name": "Upbeat Acoustic",
        "filename": "upbeat_acoustic.mp3",
        "url": "https://www.youtube.com/audiolibrary/music",
        "genre": "acoustic",
        "mood": "happy",
        "niches": ["lifestyle", "travel", "vlog"],
        "emoji": "🎸",
        "description": "Позитивная акустика - лайфстайл",
        "volume": -18
    },
    "energetic_pop": {
        "name": "Energetic Pop",
        "filename": "energetic_pop.mp3",
        "url": "https://www.youtube.com/audiolibrary/music",
        "genre": "pop",
        "mood": "energetic",
        "niches": ["entertainment", "fun", "comedy"],
        "emoji": "🎉",
        "description": "Энергичный поп - развлечения",
        "volume": -18
    },

    # ═══════════════════════════════════════════════════════════════
    # СПЕЦИАЛЬНЫЕ
    # ═══════════════════════════════════════════════════════════════
    "no_music": {
        "name": "No Music",
        "filename": None,
        "url": None,
        "genre": "none",
        "mood": "none",
        "niches": ["all"],
        "emoji": "🔇",
        "description": "Без музыки - только голос",
        "volume": 0,
        "recommended": False
    }
}


def get_recommended_music(niche: str) -> list:
    """
    Получить рекомендованную музыку для ниши

    Args:
        niche: Ниша контента (psychology, business, storytelling и т.д.)

    Returns:
        Список рекомендованных треков с метаданными
    """
    recommended = []
    for key, track in BACKGROUND_MUSIC.items():
        if key == "no_music":
            continue
        if niche in track['niches']:
            rec = {
                'key': key,
                'name': track['name'],
                'emoji': track['emoji'],
                'description': track['description'],
                'is_recommended': track.get('recommended', False)
            }
            recommended.append(rec)

    # Сортируем: рекомендованные первыми
    recommended.sort(key=lambda x: (not x['is_recommended'], x['name']))

    # Добавляем "Без музыки" в конец
    recommended.append({
        'key': 'no_music',
        'name': 'No Music',
        'emoji': '🔇',
        'description': 'Без фоновой музыки',
        'is_recommended': False
    })

    return recommended


def get_music_volume(music_key: str) -> int:
    """
    Получить рекомендованную громкость в dB

    Args:
        music_key: Ключ музыкального трека

    Returns:
        Громкость в dB (отрицательное значение)
    """
    if music_key in BACKGROUND_MUSIC:
        return BACKGROUND_MUSIC[music_key]['volume']
    return -20  # По умолчанию -20dB


def get_music_path(music_key: str) -> str:
    """
    Получить путь к музыкальному файлу

    Args:
        music_key: Ключ музыкального трека

    Returns:
        Полный путь к файлу или None
    """
    if music_key == "no_music" or music_key not in BACKGROUND_MUSIC:
        return None

    # Путь к папке с музыкой
    music_dir = os.path.join(os.path.dirname(__file__), '..', 'assets', 'music')
    filename = BACKGROUND_MUSIC[music_key]['filename']

    if filename:
        return os.path.join(music_dir, filename)
    return None


def validate_music(music_key: str) -> bool:
    """
    Проверить, существует ли музыкальный трек

    Args:
        music_key: Ключ трека для проверки

    Returns:
        True если трек существует, иначе False
    """
    return music_key in BACKGROUND_MUSIC


def get_all_music_for_ui() -> dict:
    """
    Получить все треки в формате для UI

    Returns:
        Словарь треков с метаданными для отображения
    """
    ui_music = {}
    for key, track in BACKGROUND_MUSIC.items():
        ui_music[key] = {
            'name': f"{track['emoji']} {track['name']}",
            'desc': track['description'],
            'niches': track['niches'],
            'recommended': track.get('recommended', False),
            'genre': track['genre'],
            'mood': track['mood']
        }
    return ui_music


def get_music_by_category() -> dict:
    """
    Получить музыку сгруппированную по категориям

    Returns:
        Словарь с категориями и треками
    """
    categories = {
        'psychology': {'name': 'Психология / Wellness', 'tracks': []},
        'business': {'name': 'Бизнес / Мотивация', 'tracks': []},
        'storytelling': {'name': 'Истории / Драма', 'tracks': []},
        'education': {'name': 'Образование', 'tracks': []},
        'entertainment': {'name': 'Развлечения', 'tracks': []}
    }

    for key, track in BACKGROUND_MUSIC.items():
        if key == 'no_music':
            continue
        for niche in track['niches']:
            if niche in categories:
                categories[niche]['tracks'].append({
                    'key': key,
                    'name': track['name'],
                    'emoji': track['emoji'],
                    'description': track['description'],
                    'recommended': track.get('recommended', False)
                })

    return categories
