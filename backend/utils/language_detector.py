"""
Модуль для определения языка и работы с мультиязычным контентом
"""

import re
from typing import Optional, Dict, List
from collections import Counter


class LanguageDetector:
    """Детектор языка на основе паттернов"""

    # Паттерны для определения языка
    LANGUAGE_PATTERNS = {
        'ru': r'[а-яА-ЯёЁ]',
        'en': r'[a-zA-Z]',
        'es': r'[áéíóúñÁÉÍÓÚÑ]',
        'fr': r'[àâäæçéèêëïîôùûüÿœÀÂÄÆÇÉÈÊËÏÎÔÙÛÜŸŒ]',
        'de': r'[äöüßÄÖÜ]',
        'pt': r'[ãõçÃÕÇ]',
        'it': r'[àèéìòù]',
        'ar': r'[\u0600-\u06FF]',
        'hi': r'[\u0900-\u097F]',
        'zh': r'[\u4E00-\u9FFF]',
        'ja': r'[\u3040-\u309F\u30A0-\u30FF]',
        'ko': r'[\uAC00-\uD7AF]'
    }

    LANGUAGE_NAMES = {
        'ru': 'Russian',
        'en': 'English',
        'es': 'Spanish',
        'fr': 'French',
        'de': 'German',
        'pt': 'Portuguese',
        'it': 'Italian',
        'ar': 'Arabic',
        'hi': 'Hindi',
        'zh': 'Chinese',
        'ja': 'Japanese',
        'ko': 'Korean'
    }

    # Стоп-слова для разных языков (топ-10)
    STOP_WORDS = {
        'ru': {'это', 'как', 'для', 'что', 'или', 'все', 'был', 'вас', 'где', 'его'},
        'en': {'the', 'and', 'for', 'are', 'but', 'not', 'you', 'all', 'can', 'had'},
        'es': {'los', 'las', 'del', 'por', 'para', 'con', 'una', 'más', 'que', 'sus'},
        'fr': {'les', 'des', 'une', 'pour', 'dans', 'qui', 'avec', 'sur', 'par', 'sont'},
        'de': {'der', 'die', 'und', 'den', 'das', 'von', 'ist', 'des', 'sich', 'mit'},
    }

    @classmethod
    def detect_language(cls, text: str) -> str:
        """
        Определение языка текста

        Args:
            text: Текст для анализа

        Returns:
            str: Код языка (ru, en и т.д.)
        """
        if not text:
            return 'en'

        scores = {}

        for lang, pattern in cls.LANGUAGE_PATTERNS.items():
            matches = len(re.findall(pattern, text))
            scores[lang] = matches

        # Возвращаем язык с максимальным счётом
        detected_lang = max(scores, key=scores.get)

        # Если очень мало совпадений, возвращаем английский по умолчанию
        if scores[detected_lang] < 3:
            return 'en'

        return detected_lang

    @classmethod
    def get_language_name(cls, lang_code: str) -> str:
        """Получение названия языка по коду"""
        return cls.LANGUAGE_NAMES.get(lang_code, 'Unknown')

    @classmethod
    def extract_keywords(cls, text: str, lang: str = 'auto', top_n: int = 10) -> List[str]:
        """
        Извлечение ключевых слов из текста

        Args:
            text: Текст
            lang: Язык (auto для автоопределения)
            top_n: Количество топ слов

        Returns:
            list: Список ключевых слов
        """
        if lang == 'auto':
            lang = cls.detect_language(text)

        # Извлекаем слова
        words = re.findall(r'\b\w{3,}\b', text.lower())

        # Фильтруем стоп-слова
        stop_words = cls.STOP_WORDS.get(lang, set())
        filtered_words = [w for w in words if w not in stop_words]

        # Подсчёт частоты
        word_counts = Counter(filtered_words)

        # Возвращаем топ N
        return [word for word, count in word_counts.most_common(top_n)]

    @classmethod
    def suggest_translation_needed(cls, source_lang: str, target_market: str = 'ru') -> bool:
        """
        Определить, нужен ли перевод контента

        Args:
            source_lang: Язык источника
            target_market: Целевой рынок

        Returns:
            bool: Нужен ли перевод
        """
        return source_lang != target_market

    @classmethod
    def get_adaptation_tips(cls, source_lang: str, target_lang: str) -> List[str]:
        """
        Советы по адаптации контента для целевого языка

        Args:
            source_lang: Язык источника
            target_lang: Целевой язык

        Returns:
            list: Список советов
        """
        tips = []

        if source_lang == target_lang:
            tips.append(f"✅ Контент уже на языке целевой аудитории ({cls.get_language_name(target_lang)})")
            return tips

        tips.append(f"🔄 Перевести контент с {cls.get_language_name(source_lang)} на {cls.get_language_name(target_lang)}")

        # Специфичные советы для разных языков
        if target_lang == 'ru':
            tips.append("🇷🇺 Адаптируйте заголовки: русская аудитория предпочитает более прямые названия")
            tips.append("📊 Добавьте русские субтитры - это увеличивает engagement на 25-40%")
            tips.append("🎯 Учтите культурные различия в примерах и отсылках")

        elif target_lang == 'en':
            tips.append("🇺🇸 English audience prefers catchy, curiosity-driven titles")
            tips.append("⏱ Keep videos concise - English market values time efficiency")
            tips.append("💡 Add clear value proposition in first 10 seconds")

        elif target_lang == 'es':
            tips.append("🇪🇸 Испаноязычная аудитория ценит эмоциональность")
            tips.append("🎥 Рассмотрите создание отдельных версий для разных стран (ES, MX, AR)")

        return tips
