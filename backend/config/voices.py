"""
Конфигурация голосов ElevenLabs для озвучки

Поддержка всех бесплатных голосов с распределением по нишам
"""

ELEVENLABS_VOICES = {
    # ═══════════════════════════════════════════════════════════════
    # ПСИХОЛОГИЯ / САМОРАЗВИТИЕ / WELLNESS
    # ═══════════════════════════════════════════════════════════════
    "rachel": {
        "voice_id": "21m00Tcm4TlvDq8ikWAM",
        "name": "Rachel",
        "gender": "female",
        "age": "young",
        "accent": "american",
        "description": "Теплый, дружелюбный, успокаивающий",
        "niches": ["psychology", "self-help", "meditation", "wellness"],
        "emoji": "🎭",
        "recommended": True,  # Самый популярный для психологии
        "preview_text": "Привет! Я Рэйчел, и сегодня мы поговорим о психологии отношений и внутренней гармонии."
    },
    "charlotte": {
        "voice_id": "XB0fDUnXU5powFXDhCwa",
        "name": "Charlotte",
        "gender": "female",
        "age": "middle",
        "accent": "british",
        "description": "Профессиональный, авторитетный, уверенный",
        "niches": ["psychology", "education", "professional"],
        "emoji": "👩‍🏫",
        "preview_text": "Добро пожаловать. Я Шарлотта, давайте изучим эту тему глубже и поймём суть явления."
    },
    "grace": {
        "voice_id": "oWAxZDx7w5VEj9dCyTzz",
        "name": "Grace",
        "gender": "female",
        "age": "middle",
        "accent": "american",
        "description": "Спокойный, вдумчивый, мудрый",
        "niches": ["psychology", "meditation", "spirituality"],
        "emoji": "🧘‍♀️",
        "preview_text": "Здравствуйте. Я Грейс. Давайте найдём внутренний покой и гармонию с собой."
    },

    # ═══════════════════════════════════════════════════════════════
    # БИЗНЕС / ФИНАНСЫ / МОТИВАЦИЯ
    # ═══════════════════════════════════════════════════════════════
    "adam": {
        "voice_id": "pNInz6obpgDQGcFmaJgB",
        "name": "Adam",
        "gender": "male",
        "age": "middle",
        "accent": "american",
        "description": "Уверенный, авторитетный, мотивирующий",
        "niches": ["business", "finance", "motivation", "leadership"],
        "emoji": "💼",
        "recommended": True,  # Самый популярный для бизнеса
        "preview_text": "Привет! Я Адам. Сегодня мы обсудим стратегии успеха в бизнесе и достижения целей."
    },
    "antoni": {
        "voice_id": "ErXwobaYiN019PkySvjV",
        "name": "Antoni",
        "gender": "male",
        "age": "young",
        "accent": "american",
        "description": "Энергичный, харизматичный, динамичный",
        "niches": ["business", "entrepreneurship", "marketing"],
        "emoji": "🚀",
        "preview_text": "What's up! Я Антони, и мы разберём, как масштабировать ваш бизнес до небес!"
    },
    "josh": {
        "voice_id": "TxGEqnHWrfWFTfGW9XjX",
        "name": "Josh",
        "gender": "male",
        "age": "young",
        "accent": "american",
        "description": "Дружелюбный, позитивный, вдохновляющий",
        "niches": ["motivation", "self-help", "business"],
        "emoji": "⭐",
        "preview_text": "Привет друзья! Я Джош, и сегодня мы поговорим о достижении невероятных целей!"
    },
    "arnold": {
        "voice_id": "VR6AewLTigWG4xSOukaG",
        "name": "Arnold",
        "gender": "male",
        "age": "middle",
        "accent": "american",
        "description": "Глубокий, спокойный, авторитетный",
        "niches": ["business", "finance", "documentary"],
        "emoji": "🎙️",
        "preview_text": "Здравствуйте. Я Арнольд. Давайте рассмотрим факты и проанализируем данные."
    },

    # ═══════════════════════════════════════════════════════════════
    # ИСТОРИИ / РАЗВЛЕЧЕНИЯ / ДРАМА
    # ═══════════════════════════════════════════════════════════════
    "bella": {
        "voice_id": "EXAVITQu4vr4xnSDxMaL",
        "name": "Bella",
        "gender": "female",
        "age": "young",
        "accent": "american",
        "description": "Эмоциональный, выразительный, драматичный",
        "niches": ["storytelling", "entertainment", "drama"],
        "emoji": "🎬",
        "recommended": True,  # Лучший для историй
        "preview_text": "О, вы не поверите, что случилось дальше! Я Белла, и это невероятная история!"
    },
    "elli": {
        "voice_id": "MF3mGyEYCl7XYWbV9V6O",
        "name": "Elli",
        "gender": "female",
        "age": "young",
        "accent": "american",
        "description": "Молодой, игривый, энергичный",
        "niches": ["entertainment", "kids", "casual"],
        "emoji": "🎉",
        "preview_text": "Привет всем! Я Элли, давайте повеселимся и узнаем что-то новое!"
    },
    "sam": {
        "voice_id": "yoZ06aMxZJJ28mfd3POQ",
        "name": "Sam",
        "gender": "male",
        "age": "young",
        "accent": "american",
        "description": "Динамичный, драматичный, захватывающий",
        "niches": ["storytelling", "action", "thriller"],
        "emoji": "🎭",
        "preview_text": "Внимание! Я Сэм, и то, что вы сейчас услышите, перевернёт ваш мир!"
    },

    # ═══════════════════════════════════════════════════════════════
    # ОБРАЗОВАНИЕ / НАУКА / ДОКУМЕНТАЛЬНОЕ
    # ═══════════════════════════════════════════════════════════════
    "domi": {
        "voice_id": "AZnzlk1XvdvUeBnXmlld",
        "name": "Domi",
        "gender": "female",
        "age": "young",
        "accent": "american",
        "description": "Ясный, чёткий, образовательный",
        "niches": ["education", "science", "tutorial"],
        "emoji": "📚",
        "preview_text": "Здравствуйте. Я Доми, и сегодня мы изучим новую тему шаг за шагом."
    },
    "ethan": {
        "voice_id": "g5CIjZEefAph4nQFvHAz",
        "name": "Ethan",
        "gender": "male",
        "age": "young",
        "accent": "american",
        "description": "Умный, информативный, профессиональный",
        "niches": ["education", "technology", "science"],
        "emoji": "🔬",
        "preview_text": "Добро пожаловать. Я Итан, давайте углубимся в науку и технологии."
    },

    # ═══════════════════════════════════════════════════════════════
    # ДОПОЛНИТЕЛЬНЫЕ ГОЛОСА
    # ═══════════════════════════════════════════════════════════════
    "callum": {
        "voice_id": "N2lVS1w4EtoT3dr4eOWO",
        "name": "Callum",
        "gender": "male",
        "age": "middle",
        "accent": "american",
        "description": "Спокойный, надёжный, серьёзный",
        "niches": ["documentary", "news", "professional"],
        "emoji": "📰",
        "preview_text": "Добрый день. Я Каллум, и мы рассмотрим самые важные события."
    },
    "daniel": {
        "voice_id": "onwK4e9ZLuTAKqWW03F9",
        "name": "Daniel",
        "gender": "male",
        "age": "middle",
        "accent": "british",
        "description": "Глубокий, британский, благородный",
        "niches": ["documentary", "history", "culture"],
        "emoji": "🎩",
        "preview_text": "Good evening. I'm Daniel, and we shall explore history together."
    },
    "lily": {
        "voice_id": "pFZP5JQG7iQjIQuC4Bku",
        "name": "Lily",
        "gender": "female",
        "age": "middle",
        "accent": "british",
        "description": "Элегантный, британский, утончённый",
        "niches": ["culture", "art", "history"],
        "emoji": "🌸",
        "preview_text": "Hello. I'm Lily, let's discover the beauty of art and culture."
    }
}

# Голоса для разных языков (мультиязычная поддержка)
MULTILINGUAL_VOICES = {
    # Русский
    "ru": {
        "sergey": {
            "voice_id": "pqHfZKP75CvOlQylNhV4",
            "name": "Sergey (RU)",
            "gender": "male",
            "description": "Русский мужской голос",
            "emoji": "🇷🇺",
            "preview_text": "Здравствуйте! Я Сергей, и сегодня мы поговорим на русском языке."
        }
    },
    # Испанский
    "es": {
        "diego": {
            "voice_id": "TxGEqnHWrfWFTfGW9XjX",
            "name": "Diego (ES)",
            "gender": "male",
            "description": "Испанский мужской голос",
            "emoji": "🇪🇸",
            "preview_text": "¡Hola! Soy Diego y hoy hablaremos en español."
        }
    },
    # Немецкий
    "de": {
        "klaus": {
            "voice_id": "pNInz6obpgDQGcFmaJgB",
            "name": "Klaus (DE)",
            "gender": "male",
            "description": "Немецкий мужской голос",
            "emoji": "🇩🇪",
            "preview_text": "Guten Tag! Ich bin Klaus und wir sprechen auf Deutsch."
        }
    }
}


def get_recommended_voices(niche: str) -> list:
    """
    Получить рекомендованные голоса для ниши

    Args:
        niche: Ниша контента (psychology, business, storytelling и т.д.)

    Returns:
        Список рекомендованных голосов с метаданными
    """
    recommended = []
    for key, voice in ELEVENLABS_VOICES.items():
        if niche in voice['niches']:
            rec = {
                'key': key,
                'name': voice['name'],
                'emoji': voice['emoji'],
                'description': voice['description'],
                'is_recommended': voice.get('recommended', False)
            }
            recommended.append(rec)

    # Сортируем: рекомендованные первыми
    recommended.sort(key=lambda x: (not x['is_recommended'], x['name']))
    return recommended


def get_voice_id(voice_key: str) -> str:
    """
    Получить voice_id для ElevenLabs API

    Args:
        voice_key: Ключ голоса (rachel, adam, bella и т.д.)

    Returns:
        Voice ID для API
    """
    if voice_key in ELEVENLABS_VOICES:
        return ELEVENLABS_VOICES[voice_key]['voice_id']

    # По умолчанию Rachel (самый популярный)
    print(f"⚠️ Голос '{voice_key}' не найден, использую Rachel")
    return ELEVENLABS_VOICES['rachel']['voice_id']


def get_preview_text(voice_key: str) -> str:
    """
    Получить текст для прослушки голоса

    Args:
        voice_key: Ключ голоса

    Returns:
        Текст для тестовой озвучки
    """
    if voice_key in ELEVENLABS_VOICES:
        return ELEVENLABS_VOICES[voice_key].get('preview_text', 'Hello, this is a test.')
    return 'Hello, this is a test.'


def get_all_voices_for_ui() -> dict:
    """
    Получить все голоса в формате для UI

    Returns:
        Словарь голосов с метаданными для отображения
    """
    ui_voices = {}
    for key, voice in ELEVENLABS_VOICES.items():
        ui_voices[key] = {
            'name': f"{voice['emoji']} {voice['name']}",
            'desc': voice['description'],
            'niches': voice['niches'],
            'recommended': voice.get('recommended', False),
            'gender': voice['gender'],
            'accent': voice['accent']
        }
    return ui_voices


def validate_voice(voice_key: str) -> bool:
    """
    Проверить, существует ли голос

    Args:
        voice_key: Ключ голоса для проверки

    Returns:
        True если голос существует, иначе False
    """
    return voice_key in ELEVENLABS_VOICES


def get_voices_by_category() -> dict:
    """
    Получить голоса сгруппированные по категориям

    Returns:
        Словарь с категориями и голосами
    """
    categories = {
        'psychology': {'name': 'Психология / Саморазвитие', 'voices': []},
        'business': {'name': 'Бизнес / Финансы', 'voices': []},
        'storytelling': {'name': 'Истории / Развлечения', 'voices': []},
        'education': {'name': 'Образование / Наука', 'voices': []}
    }

    for key, voice in ELEVENLABS_VOICES.items():
        for niche in voice['niches']:
            if niche in categories:
                categories[niche]['voices'].append({
                    'key': key,
                    'name': voice['name'],
                    'emoji': voice['emoji'],
                    'description': voice['description'],
                    'recommended': voice.get('recommended', False)
                })

    return categories
