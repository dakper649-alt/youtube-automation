"""
Script Generator - генерация YouTube сценариев
Поддерживает: Hugging Face (Llama/Qwen/Mistral), Groq (Llama 3.1 70B), Google Gemini 2.0 Flash, OpenAI GPT-4o-mini
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

    async def _generate_with_ollama(self, prompt: str) -> str:
        """
        Генерация через локальную Ollama модель

        Требования:
        1. Ollama должна быть установлена: brew install ollama
        2. Модель скачана: ollama pull llama3.1:8b
        3. Сервер запущен: ollama serve (в фоне)
        """

        print("   🖥️ Генерация через локальную Ollama (Llama 3.1 8B)...")

        try:
            # Ollama API endpoint (локальный)
            url = "http://localhost:11434/api/generate"

            payload = {
                "model": "llama3.1:8b",
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "num_predict": 4000,  # Максимум токенов
                }
            }

            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(url, json=payload)

                if response.status_code == 200:
                    result = response.json()
                    generated_text = result.get('response', '')

                    if generated_text:
                        print(f"   ✅ Ollama сгенерировала {len(generated_text)} символов")
                        return generated_text
                    else:
                        raise Exception("Ollama вернула пустой ответ")
                else:
                    raise Exception(f"Ollama API error: {response.status_code}")

        except httpx.ConnectError:
            raise Exception(
                "Не удалось подключиться к Ollama!\n"
                "Убедитесь что:\n"
                "1. Ollama установлена: brew install ollama\n"
                "2. Сервер запущен: ollama serve\n"
                "3. Модель скачана: ollama pull llama3.1:8b"
            )
        except Exception as e:
            raise Exception(f"Ошибка Ollama: {str(e)}")

    async def generate_script(
        self,
        topic: str,
        target_length: int = 1000,
        language: str = 'ru',
        niche: str = 'psychology',
        use_ollama: bool = True
    ) -> Dict:
        """
        Генерация сценария с приоритетом на Ollama

        Приоритет провайдеров:
        1. Ollama (локально, бесплатно) - если use_ollama=True
        2. Hugging Face (123 ключа)
        3. Groq (14,400 запросов/день)
        4. Gemini 2.0 Flash
        5. OpenAI GPT-4o-mini

        Args:
            topic: Тема видео
            target_length: Целевая длина в словах
            language: Язык ('ru' или 'en')
            niche: Ниша
            use_ollama: Использовать локальную Ollama (по умолчанию True)

        Returns:
            Dict с ключами: hook, script, cta, title_suggestions, word_count, provider, model
        """

        prompt = self._build_prompt(topic, target_length, language, niche)

        # Пробуем провайдеры по порядку: Ollama -> HF -> Groq -> Gemini -> OpenAI
        errors = []

        # 0. Попытка через Ollama (если включена)
        if use_ollama:
            try:
                print("🖥️ Пробуем Ollama (локальная Llama 3.1 8B)...")
                content = await self._generate_with_ollama(prompt)
                result = self._parse_response(content)
                result['word_count'] = len(result['script'].split())
                result['provider'] = 'ollama'
                result['model'] = 'llama3.1:8b'
                print("✅ Скрипт сгенерирован через Ollama (БЕСПЛАТНО!)")
                return result
            except Exception as e:
                print(f"⚠️  Ollama не доступна: {e}")
                print(f"   🔄 Переключаемся на облачные API...")
                errors.append(f"Ollama: {e}")

        # 1. Попытка через Hugging Face (БЕСПЛАТНО! 125 ключей!)
        try:
            print("🤗 Пробуем Hugging Face API (Llama 3.1 / Qwen / Mistral)...")
            content = await self._generate_with_huggingface(prompt)
            result = self._parse_response(content)
            result['word_count'] = len(result['script'].split())
            result['provider'] = 'huggingface'
            result['model'] = 'llama-3.1-8b'
            print("✅ Скрипт сгенерирован через Hugging Face")
            return result
        except Exception as e:
            print(f"⚠️  Hugging Face failed: {e}")
            errors.append(f"Hugging Face: {e}")

        # 2. Попытка через Groq (бесплатно)
        try:
            print("🚀 Пробуем Groq API (Llama 3.1 70B)...")
            content = await self._generate_with_groq(prompt)
            result = self._parse_response(content)
            result['word_count'] = len(result['script'].split())
            result['provider'] = 'groq'
            result['model'] = 'llama-3.1-70b'
            print("✅ Скрипт сгенерирован через Groq")
            return result
        except Exception as e:
            print(f"⚠️  Groq failed: {e}")
            errors.append(f"Groq: {e}")

        # 3. Попытка через Gemini
        try:
            print("🔄 Пробуем Gemini API (Gemini 2.0 Flash)...")
            content = await self._generate_with_gemini(prompt)
            result = self._parse_response(content)
            result['word_count'] = len(result['script'].split())
            result['provider'] = 'gemini'
            result['model'] = 'gemini-2.0-flash'
            print("✅ Скрипт сгенерирован через Gemini")
            return result
        except Exception as e:
            print(f"⚠️  Gemini failed: {e}")
            errors.append(f"Gemini: {e}")

        # 4. Попытка через OpenAI (последний fallback)
        try:
            print("🔄 Пробуем OpenAI API (GPT-4o-mini)...")
            openai_key = os.getenv('OPENAI_API_KEY')
            if not openai_key:
                raise ValueError("OPENAI_API_KEY не найден в .env")

            content = await self._generate_with_openai_direct(prompt, openai_key)
            result = self._parse_response(content)
            result['word_count'] = len(result['script'].split())
            result['provider'] = 'openai'
            result['model'] = 'gpt-4o-mini'
            print("✅ Скрипт сгенерирован через OpenAI")
            return result
        except Exception as e:
            print(f"⚠️  OpenAI failed: {e}")
            errors.append(f"OpenAI: {e}")

        # Все провайдеры упали
        raise ScriptGeneratorError(f"Все API провайдеры недоступны:\n" + "\n".join(errors))

    async def _generate_with_huggingface(self, prompt: str) -> str:
        """Генерация через Hugging Face Inference API (БЕСПЛАТНО!)"""

        # Детальное логирование для отладки
        print(f"   📊 HF Keys статистика:")
        print(f"      Всего HF ключей загружено: {len(self.key_manager.hf_keys)}")

        if len(self.key_manager.hf_keys) == 0:
            raise ValueError("❌ Нет доступных Hugging Face ключей!\nДобавьте в .env: HUGGINGFACE_API_KEY_1=hf_...")

        hf_key = self.key_manager.get_hf_key()
        print(f"      Используется ключ: {hf_key[:8]}...{hf_key[-4:]}")

        # Лучшие бесплатные модели для генерации текста
        models = [
            "meta-llama/Llama-3.1-8B-Instruct",      # Быстрая и умная
            "Qwen/Qwen2.5-72B-Instruct",             # Очень умная
            "mistralai/Mistral-7B-Instruct-v0.3"     # Надёжная
        ]

        print(f"      Пробуем {len(models)} модели по порядку...")

        for model in models:
            try:
                print(f"      🔄 Пробую модель: {model.split('/')[-1]}...")
                url = f"https://api-inference.huggingface.co/models/{model}"
                headers = {
                    "Authorization": f"Bearer {hf_key}",
                    "Content-Type": "application/json"
                }

                data = {
                    "inputs": prompt,
                    "parameters": {
                        "max_new_tokens": 4000,
                        "temperature": 0.7,
                        "top_p": 0.9,
                        "return_full_text": False
                    }
                }

                async with httpx.AsyncClient(timeout=120.0) as client:
                    response = await client.post(url, headers=headers, json=data)

                    if response.status_code == 503:
                        # Модель загружается, пробуем следующую
                        print(f"         ⏳ {model.split('/')[-1]} загружается, пробуем другую...")
                        continue

                    if response.status_code != 200:
                        error_text = response.text[:200]
                        print(f"         ❌ HTTP {response.status_code}: {error_text}")
                        continue

                    result = response.json()
                    print(f"         ✅ {model.split('/')[-1]} ответила успешно!")

                    # Hugging Face возвращает массив или объект
                    if isinstance(result, list) and len(result) > 0:
                        return result[0].get('generated_text', '')
                    elif isinstance(result, dict):
                        return result.get('generated_text', '')

            except Exception as e:
                print(f"         ⚠️  {model.split('/')[-1]} failed: {str(e)[:100]}")
                continue

        raise Exception("Все Hugging Face модели недоступны")

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
