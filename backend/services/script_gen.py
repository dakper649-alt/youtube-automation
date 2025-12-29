"""
Модуль для генерации скриптов видео с помощью AI

Функционал:
- Генерация уникальных скриптов на основе темы
- Адаптация стиля под целевую аудиторию
- Структурирование контента (вступление, основная часть, заключение)
- Оптимизация длительности скрипта
- Добавление hooks и call-to-action
- Генерация вариантов заголовков и описаний
- Генерация промптов для изображений
- Перевод скриптов на другие языки

API:
- OpenRouter API (доступ к Claude, GPT, Gemini и другим моделям)
- Поддержка бесплатных моделей (google/gemini-flash-1.5)
"""

import openai  # OpenRouter использует OpenAI-совместимый API
import asyncio
import json
import re
from typing import Dict, List, Optional
from datetime import datetime


class ScriptGeneratorError(Exception):
    """Базовый класс для ошибок генератора"""
    pass


class InvalidAPIKeyError(ScriptGeneratorError):
    """Неверный API ключ"""
    pass


class ScriptGenerator:
    """Класс для генерации скриптов видео с интеграцией OpenRouter API"""

    def __init__(self, openrouter_api_key: str, model: str = "google/gemini-flash-1.5"):
        """
        Инициализация генератора скриптов с OpenRouter

        Args:
            openrouter_api_key: API ключ OpenRouter
            model: Модель для использования (по умолчанию google/gemini-flash-1.5)

            Доступные бесплатные модели:
            - "google/gemini-flash-1.5" (РЕКОМЕНДУЕТСЯ! Быстрая и бесплатная)
            - "meta-llama/llama-3.1-8b-instruct:free"
            - "mistralai/mistral-7b-instruct:free"

            Платные дешёвые модели:
            - "anthropic/claude-3-5-haiku-20241022" ($0.25/1M токенов)
            - "openai/gpt-3.5-turbo" ($0.50/1M токенов)

        Raises:
            InvalidAPIKeyError: Если API ключ невалиден
        """
        if not openrouter_api_key or openrouter_api_key == "your_openrouter_api_key_here":
            raise InvalidAPIKeyError("Необходимо предоставить валидный OpenRouter API ключ")

        try:
            self.api_key = openrouter_api_key
            self.model = model
            self.base_url = "https://openrouter.ai/api/v1"

            # Используем OpenAI-совместимый клиент для OpenRouter
            self.client = openai.OpenAI(
                api_key=self.api_key,
                base_url=self.base_url
            )
        except Exception as e:
            raise InvalidAPIKeyError(f"Ошибка инициализации OpenRouter API: {str(e)}")

    async def generate_script(
        self,
        topic: str,
        target_length: int = 1000,
        language: str = 'ru',
        style: str = 'educational',
        tone: str = 'professional'
    ) -> Dict:
        """
        Генерирует скрипт для видео

        Args:
            topic: Тема видео
            target_length: Целевая длина в словах (по умолчанию 1000)
            language: Язык ('ru', 'en')
            style: Стиль ('educational', 'entertaining', 'documentary')
            tone: Тон ('professional', 'casual', 'humorous')

        Returns:
            dict с полями:
                - script: текст скрипта
                - word_count: количество слов
                - estimated_duration: примерная длительность в секундах
                - title_suggestions: варианты заголовков (3-5 штук)
                - hook: захватывающее начало
                - cta: призыв к действию
                - generated_at: время генерации

        Raises:
            ScriptGeneratorError: При ошибках генерации
        """
        try:
            # Строим промпт
            prompt = self._build_script_prompt(topic, target_length, style, tone, language)

            # Вызываем OpenRouter API (OpenAI-совместимый формат)
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=4096,
                temperature=0.7
            )

            # Парсим ответ
            script_text = response.choices[0].message.content

            # Извлекаем метаданные
            result = self._parse_script_response(script_text, topic)

            return result

        except openai.APIError as e:
            raise ScriptGeneratorError(f"Ошибка OpenRouter API: {str(e)}")
        except Exception as e:
            raise ScriptGeneratorError(f"Неожиданная ошибка при генерации скрипта: {str(e)}")

    def _build_script_prompt(
        self,
        topic: str,
        target_length: int,
        style: str,
        tone: str,
        language: str
    ) -> str:
        """
        Строит промпт для Claude API

        Args:
            topic: Тема видео
            target_length: Целевая длина в словах
            style: Стиль контента
            tone: Тон
            language: Язык

        Returns:
            str: Готовый промпт
        """
        lang_instructions = {
            'ru': 'на русском языке',
            'en': 'in English'
        }

        style_instructions = {
            'educational': 'образовательный стиль с объяснениями и примерами',
            'entertaining': 'развлекательный стиль с юмором и интригой',
            'documentary': 'документальный стиль с фактами и историями'
        }

        tone_instructions = {
            'professional': 'профессиональный тон, серьёзный',
            'casual': 'разговорный тон, дружелюбный',
            'humorous': 'юмористический тон, с шутками'
        }

        prompt = f"""
Создай профессиональный скрипт для YouTube видео {lang_instructions[language]}.

ТЕМА: {topic}

ТРЕБОВАНИЯ:
- Длина: примерно {target_length} слов
- Стиль: {style_instructions.get(style, style)}
- Тон: {tone_instructions.get(tone, tone)}

СТРУКТУРА СКРИПТА:
1. HOOK (10-15 секунд): Захватывающее начало, которое заставит досмотреть видео до конца
   - Интригующий вопрос ИЛИ
   - Шокирующий факт ИЛИ
   - Обещание ценности

2. ОСНОВНАЯ ЧАСТЬ: Раскрытие темы
   - Логичная структура
   - Интересные факты и примеры
   - Простые объяснения сложных вещей
   - Эмоциональные триггеры

3. ЗАКЛЮЧЕНИЕ: Завершение
   - Краткое резюме ключевых моментов
   - Призыв к действию (CTA)

ВАЖНЫЕ ПРИНЦИПЫ:
- Начни с СИЛЬНОГО хука - первые 10 секунд критичны!
- Используй короткие предложения для динамики
- Добавь эмоциональные триггеры (удивление, любопытство, польза)
- Говори на языке аудитории, без сложных терминов
- Закончи чётким призывом к действию

ФОРМАТ ОТВЕТА (строго следуй этой структуре):

[HOOK]
<Текст захватывающего начала - первые 10-15 секунд видео>

[SCRIPT]
<Полный текст скрипта от начала до конца, включая hook и заключение>

[CTA]
<Призыв к действию - что должны сделать зрители>

[TITLES]
1. <Вариант заголовка 1 - кликабельный, с интригой>
2. <Вариант заголовка 2 - с числами/вопросом>
3. <Вариант заголовка 3 - эмоциональный>
4. <Вариант заголовка 4 - с обещанием пользы>
5. <Вариант заголовка 5 - короткий и ёмкий>

Начинай генерацию!
"""

        return prompt

    def _parse_script_response(self, response_text: str, topic: str) -> Dict:
        """
        Парсит ответ Claude и извлекает структурированные данные

        Args:
            response_text: Текст ответа от Claude
            topic: Исходная тема (для fallback)

        Returns:
            dict: Структурированный результат
        """
        # Извлекаем секции
        hook = self._extract_section(response_text, 'HOOK')
        script = self._extract_section(response_text, 'SCRIPT')
        cta = self._extract_section(response_text, 'CTA')
        titles = self._extract_titles(response_text)

        # Если не удалось распарсить, используем весь текст как скрипт
        if not script:
            script = response_text

        # Если hook не извлечён, берём начало скрипта
        if not hook:
            hook = script[:200] if len(script) > 200 else script

        # Если CTA не извлечён, используем стандартный
        if not cta:
            cta = "Подпишитесь на канал, поставьте лайк и напишите в комментариях, что вы думаете об этой теме!"

        # Если заголовки не извлечены, генерируем базовый
        if not titles:
            titles = [topic]

        # Подсчёт слов и времени
        word_count = len(script.split())
        # Средняя скорость речи: 150 слов в минуту = 2.5 слова в секунду
        estimated_duration = int(word_count / 2.5)

        return {
            'script': script,
            'hook': hook,
            'cta': cta,
            'title_suggestions': titles,
            'word_count': word_count,
            'estimated_duration': estimated_duration,
            'generated_at': datetime.now().isoformat()
        }

    def _extract_section(self, text: str, section_name: str) -> Optional[str]:
        """
        Извлекает секцию из текста

        Args:
            text: Полный текст
            section_name: Название секции (HOOK, SCRIPT, CTA)

        Returns:
            str или None: Содержимое секции
        """
        # Паттерн для извлечения секции
        pattern = rf'\[{section_name}\](.*?)(?:\[|$)'
        match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)

        if match:
            return match.group(1).strip()
        return None

    def _extract_titles(self, text: str) -> List[str]:
        """
        Извлекает варианты заголовков

        Args:
            text: Полный текст

        Returns:
            list: Список заголовков
        """
        titles_section = self._extract_section(text, 'TITLES')
        if not titles_section:
            return []

        # Ищем пронумерованные строки
        titles = re.findall(r'\d+\.\s*(.+)', titles_section)
        return [t.strip() for t in titles if t.strip()]

    async def generate_image_prompts(
        self,
        script: str,
        style: str = "minimalist_stick_figure",
        images_per_minute: int = 15
    ) -> List[Dict]:
        """
        Генерирует промпты для изображений на основе скрипта

        Args:
            script: Текст скрипта
            style: Стиль изображений
            images_per_minute: Сколько изображений на минуту видео

        Returns:
            List[Dict]: Список промптов с таймкодами
            Каждый dict содержит:
                - timestamp: время в секундах
                - prompt: промпт для генерации изображения
                - scene_description: краткое описание сцены
                - duration: длительность показа изображения

        Raises:
            ScriptGeneratorError: При ошибках генерации
        """
        try:
            # Разбиваем скрипт на предложения
            sentences = self._split_into_sentences(script)

            if not sentences:
                raise ScriptGeneratorError("Скрипт пустой или не содержит предложений")

            # Вычисляем интервал между изображениями
            word_count = len(script.split())
            duration_seconds = word_count / 2.5  # ~150 слов в минуту
            image_interval = 60 / images_per_minute  # секунд на изображение

            num_images = max(1, int(duration_seconds / image_interval))
            sentences_per_image = max(1, len(sentences) // num_images)

            prompts = []
            current_time = 0

            for i in range(0, len(sentences), sentences_per_image):
                chunk = ' '.join(sentences[i:i+sentences_per_image])

                # Генерируем промпт для этого отрывка
                prompt = await self._generate_single_image_prompt(chunk, style)

                prompts.append({
                    'timestamp': round(current_time, 2),
                    'prompt': prompt,
                    'scene_description': chunk[:100],  # первые 100 символов
                    'duration': round(image_interval, 2)
                })

                current_time += image_interval

            return prompts

        except Exception as e:
            raise ScriptGeneratorError(f"Ошибка генерации промптов для изображений: {str(e)}")

    async def _generate_single_image_prompt(
        self,
        text_chunk: str,
        style: str
    ) -> str:
        """
        Генерирует детальный промпт для одного изображения

        Args:
            text_chunk: Отрывок текста скрипта
            style: Стиль изображения

        Returns:
            str: Промпт для генерации изображения
        """
        # Базовые стили
        STYLE_TEMPLATES = {
            "minimalist_stick_figure": "simple stick figure illustration, minimalist line art, {scene}, white background, black outlines, educational diagram style",
            "cinematic_photography": "cinematic photography, {scene}, dramatic lighting, film grain, professional, high detail, 4k",
            "digital_painting": "digital painting, {scene}, painterly style, rich colors, detailed illustration, artstation quality",
            "cartoon": "cartoon illustration, {scene}, bright colors, fun and friendly style, smooth lines",
            "sketch": "pencil sketch, {scene}, hand-drawn, loose linework, artistic",
            "vector": "vector art, {scene}, clean lines, flat colors, modern design",
            "3d_render": "3D render, {scene}, realistic lighting, detailed textures, octane render",
            "watercolor": "watercolor painting, {scene}, soft colors, artistic brushstrokes",
            "infographic": "infographic style, {scene}, clean layout, icons, professional design",
            "anime": "anime style, {scene}, vibrant colors, detailed characters, manga aesthetic"
        }

        base_template = STYLE_TEMPLATES.get(style, STYLE_TEMPLATES["minimalist_stick_figure"])

        try:
            # Используем Claude чтобы описать сцену
            scene_prompt = f"""
Опиши визуальную сцену для иллюстрации этого текста в 1-2 предложениях.

Текст:
"{text_chunk[:300]}"

Опиши ЧТО нужно показать на изображении:
- Персонажи (если есть)
- Действия
- Объекты
- Настроение/атмосферу

Ответ НА АНГЛИЙСКОМ ЯЗЫКЕ, кратко (максимум 50 слов), для AI генерации изображений.
Используй простые и чёткие термины.

Пример формата ответа:
"person sitting at desk with laptop, thinking, lightbulb above head, modern office setting, focused expression"

Твой ответ:
"""

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": scene_prompt}],
                max_tokens=150,
                temperature=0.5
            )

            scene_description = response.choices[0].message.content.strip()

            # Формируем финальный промпт
            final_prompt = base_template.format(scene=scene_description)

            # Добавляем детализацию
            final_prompt += ", high quality, professional composition, clear focus"

            return final_prompt

        except Exception as e:
            # Fallback: простое описание
            return base_template.format(scene=text_chunk[:100])

    def _split_into_sentences(self, text: str) -> List[str]:
        """
        Разбивает текст на предложения

        Args:
            text: Текст для разбиения

        Returns:
            List[str]: Список предложений
        """
        # Разбиение по точкам, восклицательным и вопросительным знакам
        sentences = re.split(r'[.!?]+', text)
        # Фильтруем пустые и очень короткие предложения
        return [s.strip() for s in sentences if s.strip() and len(s.strip()) > 10]

    async def translate_script(
        self,
        script: str,
        target_language: str
    ) -> Dict:
        """
        Переводит скрипт на другой язык с сохранением стиля

        Args:
            script: Исходный скрипт
            target_language: Целевой язык ('en', 'ru', 'es', 'fr', 'de', и т.д.)

        Returns:
            dict с полями:
                - script: переведённый скрипт
                - source_language: исходный язык (auto-detected)
                - target_language: целевой язык
                - word_count: количество слов

        Raises:
            ScriptGeneratorError: При ошибках перевода
        """
        lang_names = {
            'en': 'English',
            'ru': 'Russian (Русский)',
            'es': 'Spanish (Español)',
            'fr': 'French (Français)',
            'de': 'German (Deutsch)',
            'it': 'Italian (Italiano)',
            'pt': 'Portuguese (Português)',
            'ja': 'Japanese (日本語)',
            'zh': 'Chinese (中文)',
            'ko': 'Korean (한국어)'
        }

        target_lang_name = lang_names.get(target_language, target_language)

        try:
            prompt = f"""
Переведи этот скрипт для YouTube видео на {target_lang_name}.

ВАЖНЫЕ ТРЕБОВАНИЯ:
- Сохрани стиль и тон оригинала
- Адаптируй под культурный контекст целевого языка
- Сохрани эмоциональные триггеры и убедительность
- Сохрани примерно такую же длину
- НЕ добавляй ничего от себя, только перевод

ИСХОДНЫЙ СКРИПТ:
{script}

ПЕРЕВЕДЁННЫЙ СКРИПТ (только перевод, без комментариев):
"""

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=4096,
                temperature=0.3  # Низкая температура для точности перевода
            )

            translated = response.choices[0].message.content.strip()

            return {
                'script': translated,
                'source_language': 'auto',
                'target_language': target_language,
                'word_count': len(translated.split())
            }

        except Exception as e:
            raise ScriptGeneratorError(f"Ошибка перевода скрипта: {str(e)}")

    async def optimize_for_seo(
        self,
        script: str,
        primary_keywords: List[str]
    ) -> Dict:
        """
        Оптимизирует скрипт для SEO

        Args:
            script: Исходный скрипт
            primary_keywords: Список ключевых слов для SEO

        Returns:
            dict с полями:
                - optimized_script: оптимизированный скрипт
                - keyword_density: плотность ключевых слов
                - seo_title: SEO-оптимизированный заголовок
                - seo_description: Описание для YouTube
                - tags: Рекомендованные теги

        Raises:
            ScriptGeneratorError: При ошибках оптимизации
        """
        try:
            keywords_str = ", ".join(primary_keywords)

            prompt = f"""
Оптимизируй этот скрипт для YouTube SEO.

КЛЮЧЕВЫЕ СЛОВА: {keywords_str}

ЗАДАЧИ:
1. Естественно интегрируй ключевые слова в скрипт (без спама!)
2. Создай SEO-заголовок (до 60 символов)
3. Создай описание для YouTube (2-3 предложения)
4. Предложи 10 тегов для видео

ИСХОДНЫЙ СКРИПТ:
{script}

ФОРМАТ ОТВЕТА:

[OPTIMIZED_SCRIPT]
<оптимизированный скрипт>

[SEO_TITLE]
<заголовок до 60 символов>

[DESCRIPTION]
<описание для YouTube>

[TAGS]
тег1, тег2, тег3, тег4, тег5, тег6, тег7, тег8, тег9, тег10
"""

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=4096,
                temperature=0.5
            )

            result_text = response.choices[0].message.content

            # Парсим результат
            optimized_script = self._extract_section(result_text, 'OPTIMIZED_SCRIPT') or script
            seo_title = self._extract_section(result_text, 'SEO_TITLE') or "Untitled"
            description = self._extract_section(result_text, 'DESCRIPTION') or ""
            tags_text = self._extract_section(result_text, 'TAGS') or ""

            # Парсим теги
            tags = [tag.strip() for tag in tags_text.split(',') if tag.strip()]

            # Подсчёт плотности ключевых слов
            keyword_density = self._calculate_keyword_density(optimized_script, primary_keywords)

            return {
                'optimized_script': optimized_script,
                'keyword_density': keyword_density,
                'seo_title': seo_title,
                'seo_description': description,
                'tags': tags
            }

        except Exception as e:
            raise ScriptGeneratorError(f"Ошибка SEO-оптимизации: {str(e)}")

    def _calculate_keyword_density(self, text: str, keywords: List[str]) -> Dict[str, float]:
        """
        Вычисляет плотность ключевых слов

        Args:
            text: Текст для анализа
            keywords: Список ключевых слов

        Returns:
            dict: {keyword: density_percentage}
        """
        text_lower = text.lower()
        total_words = len(text.split())

        density = {}
        for keyword in keywords:
            count = text_lower.count(keyword.lower())
            density[keyword] = round((count / total_words * 100), 2) if total_words > 0 else 0.0

        return density
