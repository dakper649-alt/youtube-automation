"""
Subtitle Generator - генератор субтитров с 5 профессиональными стилями
Стили: Highlighted Words, Typewriter, Karaoke, Modern Minimalist, 3D Pop-out
"""

from typing import List, Dict, Tuple
import re


class SubtitleStyle:
    """Базовый класс для стиля субтитров"""

    def __init__(self):
        self.name = "Base Style"
        self.max_words_per_line = 10
        self.max_lines = 2

    def generate_srt(
        self,
        text: str,
        audio_duration: float,
        words_per_second: float = 2.5
    ) -> str:
        """
        Генерирует SRT файл

        Args:
            text: Текст для субтитров
            audio_duration: Длительность аудио (секунды)
            words_per_second: Скорость речи (слов в секунду)

        Returns:
            Содержимое SRT файла
        """

        # Разбиваем на слова
        words = text.split()
        total_words = len(words)

        # Вычисляем timing
        time_per_word = 1.0 / words_per_second

        # Группируем слова в субтитры
        subtitles = []
        current_time = 0.0

        i = 0
        while i < total_words:
            # Берём до max_words_per_line слов
            chunk_words = words[i:i + self.max_words_per_line]
            chunk_text = ' '.join(chunk_words)

            # Вычисляем длительность
            chunk_duration = len(chunk_words) * time_per_word
            end_time = min(current_time + chunk_duration, audio_duration)

            subtitles.append({
                'start': current_time,
                'end': end_time,
                'text': chunk_text
            })

            current_time = end_time
            i += len(chunk_words)

        # Генерируем SRT
        srt_content = self._generate_srt_content(subtitles)

        return srt_content

    def _generate_srt_content(self, subtitles: List[Dict]) -> str:
        """Генерирует содержимое SRT файла"""

        srt_lines = []

        for i, subtitle in enumerate(subtitles, 1):
            # Номер
            srt_lines.append(str(i))

            # Timing
            start_time = self._format_srt_time(subtitle['start'])
            end_time = self._format_srt_time(subtitle['end'])
            srt_lines.append(f"{start_time} --> {end_time}")

            # Текст
            srt_lines.append(subtitle['text'])

            # Пустая строка
            srt_lines.append('')

        return '\n'.join(srt_lines)

    def _format_srt_time(self, seconds: float) -> str:
        """Форматирует время в SRT формат (HH:MM:SS,mmm)"""

        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millis = int((seconds % 1) * 1000)

        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"

    def get_style_config(self) -> Dict:
        """Возвращает конфигурацию стиля для MoviePy"""
        raise NotImplementedError("Subclass must implement get_style_config()")


class HighlightedWordsStyle(SubtitleStyle):
    """
    Стиль 1: Highlighted Words (РЕКОМЕНДУЕТСЯ!)
    Белый текст с чёрной обводкой + жёлтое выделение ключевых слов
    """

    def __init__(self):
        super().__init__()
        self.name = "Highlighted Words"
        self.max_words_per_line = 8

    def get_style_config(self) -> Dict:
        return {
            'font': 'Montserrat-Bold',
            'fontsize': 70,
            'color': 'white',
            'stroke_color': 'black',
            'stroke_width': 3,
            'method': 'caption',
            'align': 'center',
            'bg_color': None,
            'highlight_color': 'yellow',  # Для ключевых слов
            'position': ('center', 'bottom'),
            'margin': (0, 100)  # Отступ от низа
        }


class TypewriterStyle(SubtitleStyle):
    """
    Стиль 2: Typewriter Effect
    Шрифт Courier New, буквы появляются по одной
    """

    def __init__(self):
        super().__init__()
        self.name = "Typewriter"
        self.max_words_per_line = 12

    def get_style_config(self) -> Dict:
        return {
            'font': 'Courier-New-Bold',
            'fontsize': 60,
            'color': 'white',
            'stroke_color': 'black',
            'stroke_width': 2,
            'method': 'caption',
            'align': 'center',
            'animation': 'typewriter',  # Эффект печатной машинки
            'position': ('center', 'bottom'),
            'margin': (0, 100)
        }


class KaraokeStyle(SubtitleStyle):
    """
    Стиль 3: Karaoke Style
    Слова меняют цвет по мере произнесения
    """

    def __init__(self):
        super().__init__()
        self.name = "Karaoke"
        self.max_words_per_line = 10

    def get_style_config(self) -> Dict:
        return {
            'font': 'Arial-Bold',
            'fontsize': 65,
            'color': 'white',
            'inactive_color': 'rgba(255,255,255,0.5)',  # Полупрозрачный
            'active_color': 'yellow',  # Текущее слово
            'past_color': 'white',  # Произнесённые слова
            'stroke_color': 'black',
            'stroke_width': 2,
            'method': 'caption',
            'align': 'center',
            'animation': 'karaoke',
            'position': ('center', 'bottom'),
            'margin': (0, 100)
        }


class ModernMinimalistStyle(SubtitleStyle):
    """
    Стиль 4: Modern Minimalist
    Тонкий шрифт, тень вместо обводки, полупрозрачный фон
    """

    def __init__(self):
        super().__init__()
        self.name = "Modern Minimalist"
        self.max_words_per_line = 12

    def get_style_config(self) -> Dict:
        return {
            'font': 'Helvetica-Neue-Light',
            'fontsize': 55,
            'color': 'white',
            'stroke_color': None,  # Без обводки
            'stroke_width': 0,
            'method': 'caption',
            'align': 'center',
            'bg_color': 'rgba(0,0,0,0.5)',  # Полупрозрачный чёрный фон
            'shadow': True,
            'shadow_color': 'rgba(0,0,0,0.7)',
            'shadow_offset': (2, 2),
            'position': ('center', 'bottom'),
            'margin': (0, 120)
        }


class PopOut3DStyle(SubtitleStyle):
    """
    Стиль 5: 3D Pop-out
    Объёмный текст с градиентом и анимацией появления
    """

    def __init__(self):
        super().__init__()
        self.name = "3D Pop-out"
        self.max_words_per_line = 6  # Меньше слов для большего размера

    def get_style_config(self) -> Dict:
        return {
            'font': 'Impact',
            'fontsize': 90,
            'color': 'linear-gradient(yellow, orange)',  # Градиент
            'stroke_color': 'black',
            'stroke_width': 4,
            'method': 'caption',
            'align': 'center',
            'animation': 'bounce',  # Эффект выпрыгивания
            '3d_effect': True,
            'extrude_depth': 3,
            'position': ('center', 'center'),  # По центру экрана
            'margin': (0, 0)
        }


class SubtitleGenerator:
    """Главный класс генератора субтитров"""

    def __init__(self):
        self.styles = {
            'highlighted_words': HighlightedWordsStyle(),
            'typewriter': TypewriterStyle(),
            'karaoke': KaraokeStyle(),
            'modern_minimalist': ModernMinimalistStyle(),
            'popout_3d': PopOut3DStyle()
        }

    def generate_subtitles(
        self,
        text: str,
        audio_duration: float,
        style_name: str = 'highlighted_words',
        output_path: str = None
    ) -> Tuple[str, Dict]:
        """
        Генерирует субтитры в заданном стиле

        Args:
            text: Текст для субтитров
            audio_duration: Длительность аудио
            style_name: Название стиля
            output_path: Путь для сохранения SRT (опционально)

        Returns:
            (srt_content, style_config)
        """

        print(f"\n📝 Генерация субтитров...")

        # Получаем стиль
        if style_name not in self.styles:
            print(f"   ⚠️ Стиль '{style_name}' не найден, использую 'highlighted_words'")
            style_name = 'highlighted_words'

        style = self.styles[style_name]

        print(f"   Стиль: {style.name}")

        # Генерируем SRT
        srt_content = style.generate_srt(text, audio_duration)

        # Сохраняем если указан путь
        if output_path:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(srt_content)
            print(f"   ✅ SRT сохранён: {output_path}")

        # Возвращаем содержимое и конфигурацию стиля
        style_config = style.get_style_config()

        return srt_content, style_config

    def get_style_recommendations(self, niche: str) -> List[str]:
        """Рекомендует стили субтитров для ниши"""

        niche_lower = niche.lower()

        recommendations = {
            'psychology': ['highlighted_words', 'modern_minimalist'],
            'education': ['highlighted_words', 'typewriter'],
            'business': ['modern_minimalist', 'highlighted_words'],
            'entertainment': ['popout_3d', 'karaoke'],
            'tech': ['modern_minimalist', 'typewriter'],
            'gaming': ['popout_3d', 'karaoke'],
            'motivation': ['popout_3d', 'highlighted_words'],
            'documentary': ['modern_minimalist', 'highlighted_words'],
            'stories': ['typewriter', 'highlighted_words']
        }

        for key, styles in recommendations.items():
            if key in niche_lower:
                return styles

        # По умолчанию
        return ['highlighted_words', 'modern_minimalist']
