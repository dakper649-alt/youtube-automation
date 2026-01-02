"""
Script Generator - генерация YouTube сценариев
Поддерживает: Groq (Llama 3.1 70B), Google Gemini 2.0 Flash, OpenAI GPT-4o-mini
"""

import os
from typing import Dict, List, Optional
import time
import httpx

# Новая библиотека Gemini
from google import genai
from google.genai import types

# OpenAI для fallback
from openai import OpenAI

class ScriptGeneratorError(Exception):
    """Ошибка генерации скрипта"""
    pass

class ScriptGenerator:
    """Генератор YouTube сценариев"""

    def __init__(self, api_key_manager, provider: str = 'gemini'):
        """
        Args:
            api_key_manager: SafeAPIManager instance
            provider: 'gemini' или 'openai'
        """
        self.key_manager = api_key_manager
        self.provider = provider.lower()

        # Gemini setup (новая библиотека)
        if self.provider == 'gemini':
            gemini_key = self.key_manager.get_gemini_key()
            if not gemini_key:
                raise ScriptGeneratorError("Нет доступных Gemini API ключей")

            self.client = genai.Client(api_key=gemini_key)
            self.model_id = 'gemini-2.0-flash-exp'
            print(f"✅ ScriptGenerator: используется Gemini 2.0 Flash")

        # OpenAI setup (fallback)
        elif self.provider == 'openai':
            openai_key = os.getenv('OPENAI_API_KEY')
            if not openai_key:
                raise ScriptGeneratorError("Нет OPENAI_API_KEY в .env")

            self.client = OpenAI(api_key=openai_key)
            print(f"✅ ScriptGenerator: используется OpenAI GPT-4o-mini")

        else:
            raise ScriptGeneratorError(f"Неизвестный provider: {provider}")

    async def generate_script(
        self,
        topic: str,
        target_length: int = 1000,
        language: str = 'ru',
        niche: str = 'psychology'
    ) -> Dict:
        """
        Генерация сценария

        Args:
            topic: Тема видео
            target_length: Целевая длина в словах
            language: Язык ('ru' или 'en')
            niche: Ниша

        Returns:
            Dict с ключами: hook, script, cta, title_suggestions, word_count
        """

        prompt = self._build_prompt(topic, target_length, language, niche)

        # Пробуем провайдеры по порядку: Groq -> Gemini -> OpenAI
        errors = []

        # 1. Попытка через Groq (быстрее и бесплатно)
        try:
            print("🚀 Пробуем Groq API (Llama 3.1 70B)...")
            content = await self._generate_with_groq(prompt)
            result = self._parse_response(content)
            result['word_count'] = len(result['script'].split())
            print("✅ Скрипт сгенерирован через Groq")
            return result
        except Exception as e:
            print(f"⚠️  Groq failed: {e}")
            errors.append(f"Groq: {e}")

        # 2. Попытка через Gemini
        try:
            print("🔄 Пробуем Gemini API (Gemini 2.0 Flash)...")
            content = await self._generate_with_gemini(prompt)
            result = self._parse_response(content)
            result['word_count'] = len(result['script'].split())
            print("✅ Скрипт сгенерирован через Gemini")
            return result
        except Exception as e:
            print(f"⚠️  Gemini failed: {e}")
            errors.append(f"Gemini: {e}")

        # 3. Попытка через OpenAI (последний fallback)
        try:
            print("🔄 Пробуем OpenAI API (GPT-4o-mini)...")
            openai_key = os.getenv('OPENAI_API_KEY')
            if not openai_key:
                raise ValueError("OPENAI_API_KEY не найден в .env")

            content = await self._generate_with_openai_direct(prompt, openai_key)
            result = self._parse_response(content)
            result['word_count'] = len(result['script'].split())
            print("✅ Скрипт сгенерирован через OpenAI")
            return result
        except Exception as e:
            print(f"⚠️  OpenAI failed: {e}")
            errors.append(f"OpenAI: {e}")

        # Все провайдеры упали
        raise ScriptGeneratorError(f"Все API провайдеры недоступны:\n" + "\n".join(errors))

    async def _generate_with_groq(self, prompt: str) -> str:
        """Генерация через Groq API (Llama 3.1 70B)"""

        groq_key = self.key_manager.get_groq_key()
        if not groq_key:
            raise ValueError("Нет доступных Groq API ключей!")

        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {groq_key}",
            "Content-Type": "application/json"
        }

        data = {
            "model": "llama-3.1-70b-versatile",
            "messages": [
                {"role": "system", "content": "Ты профессиональный YouTube сценарист."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7,
            "max_tokens": 4000
        }

        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(url, headers=headers, json=data)
            response.raise_for_status()
            result = response.json()
            return result['choices'][0]['message']['content']

    async def _generate_with_gemini(self, prompt: str) -> str:
        """Генерация через новый Gemini API"""

        response = self.client.models.generate_content(
            model=self.model_id,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.9,
                max_output_tokens=3000,
                response_modalities=['TEXT']
            )
        )

        return response.text

    async def _generate_with_openai(self, prompt: str) -> str:
        """Генерация через OpenAI"""

        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Ты профессиональный YouTube сценарист."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.9,
            max_tokens=3000
        )

        return response.choices[0].message.content

    async def _generate_with_openai_direct(self, prompt: str, api_key: str) -> str:
        """Прямая генерация через OpenAI (для fallback)"""

        client = OpenAI(api_key=api_key)

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Ты профессиональный YouTube сценарист."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.9,
            max_tokens=3000
        )

        return response.choices[0].message.content

    def _build_prompt(
        self,
        topic: str,
        target_length: int,
        language: str,
        niche: str
    ) -> str:
        """Построение промпта для AI"""

        lang_instruction = "на русском языке" if language == 'ru' else "in English"

        prompt = f"""
Создай профессиональный YouTube сценарий {lang_instruction} для видео на тему:
"{topic}"

НИША: {niche}
ЦЕЛЕВАЯ ДЛИНА: ~{target_length} слов

СТРУКТУРА СЦЕНАРИЯ:

[HOOK]
(Напиши цепляющий hook на 2-3 предложения, который заставит зрителя продолжить смотреть)

[SCRIPT]
(Напиши основной сценарий длиной ~{target_length} слов.
Используй:
- Конкретные примеры
- Истории
- Статистику
- Практические советы
- Эмоциональные триггеры
Раздели на логические блоки с подзаголовками)

[CTA]
(Напиши призыв к действию на 2-3 предложения: подписка, лайк, комментарии)

[TITLES]
(Предложи 3 варианта заголовков для видео)

ВАЖНО:
- Пиши разговорным языком
- Используй короткие предложения
- Избегай сложных терминов
- Делай паузы для подчёркивания важных моментов
"""

        return prompt.strip()

    def _parse_response(self, content: str) -> Dict:
        """Парсинг ответа AI"""

        result = {
            'hook': '',
            'script': '',
            'cta': '',
            'title_suggestions': []
        }

        # Парсинг секций
        sections = {
            'hook': ('[HOOK]', '[SCRIPT]'),
            'script': ('[SCRIPT]', '[CTA]'),
            'cta': ('[CTA]', '[TITLES]'),
            'titles': ('[TITLES]', None)
        }

        for key, (start_marker, end_marker) in sections.items():
            try:
                start_idx = content.find(start_marker)
                if start_idx == -1:
                    continue

                start_idx += len(start_marker)

                if end_marker:
                    end_idx = content.find(end_marker, start_idx)
                    if end_idx == -1:
                        section_text = content[start_idx:]
                    else:
                        section_text = content[start_idx:end_idx]
                else:
                    section_text = content[start_idx:]

                section_text = section_text.strip()

                if key == 'titles':
                    # Парсинг заголовков
                    lines = [line.strip() for line in section_text.split('\n') if line.strip()]
                    titles = []
                    for line in lines:
                        # Убираем номера и маркеры
                        clean_line = line.lstrip('0123456789.-) ').strip()
                        if clean_line:
                            titles.append(clean_line)
                    result['title_suggestions'] = titles[:3]
                else:
                    result[key] = section_text

            except Exception as e:
                print(f"⚠️ Ошибка парсинга секции {key}: {e}")

        # Валидация
        if not result['script']:
            raise ScriptGeneratorError("Не удалось распарсить сценарий")

        return result
