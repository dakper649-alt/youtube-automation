"""
Voice Manager - профессиональная озвучка через ElevenLabs
Все бесплатные голоса, автоматическая обрезка пауз, нормализация громкости
"""

import os
import asyncio
from typing import Dict, List, Optional
import requests
from pydub import AudioSegment
from pydub.silence import detect_nonsilent
import io


class VoiceManager:
    """
    Менеджер голосовой озвучки

    Возможности:
    - Все бесплатные голоса ElevenLabs
    - Автоматическая обрезка пауз
    - Нормализация громкости
    - Рекомендации голосов по нишам
    - Интеграция с SafeAPIManager
    """

    def __init__(self, api_key_manager, text_normalizer):
        self.key_manager = api_key_manager
        self.normalizer = text_normalizer

        # ElevenLabs API endpoint
        self.api_url = "https://api.elevenlabs.io/v1/text-to-speech"

        # Все бесплатные голоса ElevenLabs с характеристиками
        self.voices = self._init_voices()

    def _init_voices(self) -> Dict:
        """
        Инициализация всех бесплатных голосов ElevenLabs

        Каждый голос имеет:
        - voice_id: ID в ElevenLabs
        - name: Имя голоса
        - gender: Пол (male/female)
        - accent: Акцент (american/british/neutral)
        - age: Возраст (young/middle/old)
        - style: Стиль (narrative/conversational/energetic/calm)
        - best_for: Рекомендуемые ниши
        """

        return {
            # ═══════════════════════════════════════════════════════════
            # МУЖСКИЕ ГОЛОСА
            # ═══════════════════════════════════════════════════════════

            "adam": {
                "voice_id": "pNInz6obpgDQGcFmaJgB",
                "name": "Adam",
                "gender": "male",
                "accent": "american",
                "age": "middle",
                "style": "narrative",
                "description": "Глубокий нарративный голос",
                "best_for": ["documentary", "history", "serious", "education", "audiobooks"]
            },

            "antoni": {
                "voice_id": "ErXwobaYiN019PkySvjV",
                "name": "Antoni",
                "gender": "male",
                "accent": "american",
                "age": "young",
                "style": "energetic",
                "description": "Энергичный молодой голос",
                "best_for": ["tech", "startups", "modern", "youtube", "entertainment"]
            },

            "arnold": {
                "voice_id": "VR6AewLTigWG4xSOukaG",
                "name": "Arnold",
                "gender": "male",
                "accent": "american",
                "age": "middle",
                "style": "crisp",
                "description": "Чёткий американский голос",
                "best_for": ["news", "business", "corporate", "professional"]
            },

            "callum": {
                "voice_id": "N2lVS1w4EtoT3dr4eOWO",
                "name": "Callum",
                "gender": "male",
                "accent": "american",
                "age": "middle",
                "style": "conversational",
                "description": "Разговорный дружелюбный",
                "best_for": ["podcasts", "interviews", "casual", "lifestyle"]
            },

            "charlie": {
                "voice_id": "IKne3meq5aSn9XLyUdCD",
                "name": "Charlie",
                "gender": "male",
                "accent": "australian",
                "age": "middle",
                "style": "casual",
                "description": "Австралийский непринуждённый",
                "best_for": ["travel", "adventure", "lifestyle", "fun"]
            },

            "clyde": {
                "voice_id": "2EiwWnXFnvU5JabPnv8n",
                "name": "Clyde",
                "gender": "male",
                "accent": "american",
                "age": "middle",
                "style": "warm",
                "description": "Тёплый американский голос",
                "best_for": ["meditation", "wellness", "calm", "spiritual"]
            },

            "daniel": {
                "voice_id": "onwK4e9ZLuTAKqWW03F9",
                "name": "Daniel",
                "gender": "male",
                "accent": "british",
                "age": "middle",
                "style": "authoritative",
                "description": "Авторитетный британский",
                "best_for": ["documentary", "education", "serious", "formal"]
            },

            "ethan": {
                "voice_id": "g5CIjZEefAph4nQFvHAz",
                "name": "Ethan",
                "gender": "male",
                "accent": "american",
                "age": "young",
                "style": "clear",
                "description": "Ясный молодой голос",
                "best_for": ["education", "explainer", "tutorials", "tech"]
            },

            "fin": {
                "voice_id": "D38z5RcWu1voky8WS1ja",
                "name": "Fin",
                "gender": "male",
                "accent": "irish",
                "age": "old",
                "style": "sailor",
                "description": "Ирландский морской волк",
                "best_for": ["stories", "adventure", "history", "tales"]
            },

            "george": {
                "voice_id": "JBFqnCBsd6RMkjVDRZzb",
                "name": "George",
                "gender": "male",
                "accent": "british",
                "age": "middle",
                "style": "warm",
                "description": "Тёплый британский",
                "best_for": ["audiobooks", "narration", "calm", "cozy"]
            },

            "harry": {
                "voice_id": "SOYHLrjzK2X1ezoPC6cr",
                "name": "Harry",
                "gender": "male",
                "accent": "american",
                "age": "young",
                "style": "anxious",
                "description": "Тревожный молодой",
                "best_for": ["thriller", "mystery", "suspense", "drama"]
            },

            "james": {
                "voice_id": "ZQe5CZNOzWyzPSCn5a3c",
                "name": "James",
                "gender": "male",
                "accent": "australian",
                "age": "old",
                "style": "calm",
                "description": "Спокойный австралийский старший",
                "best_for": ["wisdom", "meditation", "calm", "advice"]
            },

            "jeremy": {
                "voice_id": "bVMeCyTHy58xNoL34h3p",
                "name": "Jeremy",
                "gender": "male",
                "accent": "irish",
                "age": "young",
                "style": "excited",
                "description": "Взволнованный ирландский",
                "best_for": ["entertainment", "gaming", "fun", "energetic"]
            },

            "joseph": {
                "voice_id": "Zlb1dXrM653N07WRdFW3",
                "name": "Joseph",
                "gender": "male",
                "accent": "british",
                "age": "middle",
                "style": "professional",
                "description": "Профессиональный британский",
                "best_for": ["business", "corporate", "formal", "news"]
            },

            "josh": {
                "voice_id": "TxGEqnHWrfWFTfGW9XjX",
                "name": "Josh",
                "gender": "male",
                "accent": "american",
                "age": "young",
                "style": "conversational",
                "description": "Разговорный американский молодой",
                "best_for": ["podcasts", "casual", "friendly", "modern"]
            },

            "liam": {
                "voice_id": "TX3LPaxmHKxFdv7VOQHJ",
                "name": "Liam",
                "gender": "male",
                "accent": "american",
                "age": "young",
                "style": "neutral",
                "description": "Нейтральный американский",
                "best_for": ["general", "versatile", "explainer", "tutorials"]
            },

            "michael": {
                "voice_id": "flq6f7yk4E4fJM5XTYuZ",
                "name": "Michael",
                "gender": "male",
                "accent": "american",
                "age": "old",
                "style": "authoritative",
                "description": "Авторитетный старший американский",
                "best_for": ["documentary", "serious", "formal", "authority"]
            },

            "thomas": {
                "voice_id": "GBv7mTt0atIp3Br8iCZE",
                "name": "Thomas",
                "gender": "male",
                "accent": "american",
                "age": "young",
                "style": "calm",
                "description": "Спокойный молодой американский",
                "best_for": ["meditation", "calm", "soothing", "wellness"]
            },

            # ═══════════════════════════════════════════════════════════
            # ЖЕНСКИЕ ГОЛОСА
            # ═══════════════════════════════════════════════════════════

            "rachel": {
                "voice_id": "21m00Tcm4TlvDq8ikWAM",
                "name": "Rachel",
                "gender": "female",
                "accent": "american",
                "age": "young",
                "style": "calm",
                "description": "Спокойный женский голос",
                "best_for": ["meditation", "wellness", "calm", "gentle", "psychology"]
            },

            "domi": {
                "voice_id": "AZnzlk1XvdvUeBnXmlld",
                "name": "Domi",
                "gender": "female",
                "accent": "american",
                "age": "young",
                "style": "strong",
                "description": "Сильный уверенный женский",
                "best_for": ["motivation", "fitness", "empowerment", "strong"]
            },

            "bella": {
                "voice_id": "EXAVITQu4vr4xnSDxMaL",
                "name": "Bella",
                "gender": "female",
                "accent": "american",
                "age": "young",
                "style": "soft",
                "description": "Мягкий американский женский",
                "best_for": ["audiobooks", "stories", "gentle", "children"]
            },

            "elli": {
                "voice_id": "MF3mGyEYCl7XYWbV9V6O",
                "name": "Elli",
                "gender": "female",
                "accent": "american",
                "age": "young",
                "style": "emotional",
                "description": "Эмоциональный женский",
                "best_for": ["drama", "emotional", "stories", "personal"]
            },

            "emily": {
                "voice_id": "LcfcDJNUP1GQjkzn1xUU",
                "name": "Emily",
                "gender": "female",
                "accent": "american",
                "age": "middle",
                "style": "calm",
                "description": "Спокойный средний женский",
                "best_for": ["meditation", "wellness", "calm", "professional"]
            },

            "grace": {
                "voice_id": "oWAxZDx7w5VEj9dCyTzz",
                "name": "Grace",
                "gender": "female",
                "accent": "american-southern",
                "age": "young",
                "style": "warm",
                "description": "Тёплый южно-американский",
                "best_for": ["stories", "friendly", "warm", "personal"]
            },

            "jessica": {
                "voice_id": "cgSgspJ2msm6clMCkdW9",
                "name": "Jessica",
                "gender": "female",
                "accent": "american",
                "age": "young",
                "style": "expressive",
                "description": "Выразительный американский",
                "best_for": ["entertainment", "expressive", "dynamic", "fun"]
            },

            "matilda": {
                "voice_id": "XrExE9yKIg1WjnnlVkGX",
                "name": "Matilda",
                "gender": "female",
                "accent": "american",
                "age": "middle",
                "style": "warm",
                "description": "Тёплый средний женский",
                "best_for": ["audiobooks", "narration", "cozy", "friendly"]
            },

            "nicole": {
                "voice_id": "piTKgcLEGmPE4e6mEKli",
                "name": "Nicole",
                "gender": "female",
                "accent": "american",
                "age": "young",
                "style": "whispery",
                "description": "Шепчущий женский голос",
                "best_for": ["asmr", "intimate", "gentle", "soothing"]
            },

            "sarah": {
                "voice_id": "EXAVITQu4vr4xnSDxMaL",
                "name": "Sarah",
                "gender": "female",
                "accent": "american",
                "age": "young",
                "style": "soft",
                "description": "Мягкий молодой женский",
                "best_for": ["stories", "gentle", "calm", "friendly"]
            }
        }

    async def generate_audio(
        self,
        text: str,
        voice_id: str,
        output_path: str,
        normalize_text: bool = True,
        remove_silence: bool = True,
        normalize_volume: bool = True
    ) -> str:
        """
        Генерирует аудио с профессиональной обработкой

        Args:
            text: Текст для озвучки
            voice_id: ID голоса (или имя из self.voices)
            output_path: Путь для сохранения
            normalize_text: Нормализовать текст перед озвучкой
            remove_silence: Обрезать длинные паузы
            normalize_volume: Нормализовать громкость

        Returns:
            Путь к сгенерированному файлу
        """

        print(f"\n🎙️  Генерация аудио...")

        # Если передано имя голоса вместо ID - конвертируем
        if voice_id in self.voices:
            voice_config = self.voices[voice_id]
            actual_voice_id = voice_config['voice_id']
            print(f"   Голос: {voice_config['name']} ({voice_config['description']})")
        else:
            actual_voice_id = voice_id
            print(f"   Голос ID: {voice_id}")

        # 1. Нормализация текста (КРИТИЧНО!)
        if normalize_text:
            print(f"   🔧 Нормализация текста...")
            text = self.normalizer.normalize_for_tts(text)

            # Валидация
            validation = self.normalizer.validate_for_tts(text)

            if not validation['is_valid']:
                print(f"   ⚠️  ПРОБЛЕМЫ С ТЕКСТОМ:")
                for issue in validation['issues']:
                    print(f"      ❌ {issue}")

            if validation['warnings']:
                print(f"   ⚠️  Предупреждения:")
                for warning in validation['warnings']:
                    print(f"      ⚠️  {warning}")

            print(f"   ✅ Текст нормализован ({validation['word_count']} слов)")

        # 2. Генерация через ElevenLabs
        print(f"   🎵 Генерация аудио через ElevenLabs...")

        # Получаем API ключ
        api_key = await self.key_manager.get_safe_elevenlabs_key()

        url = f"{self.api_url}/{actual_voice_id}"

        headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": api_key
        }

        data = {
            "text": text,
            "model_id": "eleven_monolingual_v1",
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.75,
                "style": 0.0,
                "use_speaker_boost": True
            }
        }

        try:
            response = requests.post(url, json=data, headers=headers, timeout=120)

            if response.status_code == 200:
                # Сохраняем raw аудио
                temp_path = output_path.replace('.mp3', '_temp.mp3')
                with open(temp_path, 'wb') as f:
                    f.write(response.content)

                # Трекаем использование (считаем символы)
                chars_used = len(text)
                self.key_manager.track_usage('elevenlabs', api_key, chars_used)

                print(f"   ✅ Аудио сгенерировано ({chars_used} символов)")

                # 3. Обработка аудио
                audio = AudioSegment.from_mp3(temp_path)

                # 3.1 Обрезка длинных пауз (КРИТИЧНО!)
                if remove_silence:
                    print(f"   ✂️  Обрезка пауз...")
                    audio = self._remove_long_silences(audio)

                # 3.2 Нормализация громкости
                if normalize_volume:
                    print(f"   🔊 Нормализация громкости...")
                    audio = self._normalize_volume(audio)

                # 3.3 Fade in/out (плавное начало и конец)
                audio = audio.fade_in(100).fade_out(100)

                # Сохраняем финальное аудио
                audio.export(output_path, format="mp3", bitrate="192k")

                # Удаляем temp файл
                if os.path.exists(temp_path):
                    os.remove(temp_path)

                duration = len(audio) / 1000.0  # в секундах
                print(f"   ✅ Аудио готово: {output_path}")
                print(f"   ⏱️  Длительность: {duration:.1f}s")

                return output_path

            else:
                error_msg = f"ElevenLabs API error: {response.status_code}"
                print(f"   ❌ {error_msg}")
                print(f"   {response.text}")

                # Отмечаем ошибку
                self.key_manager.mark_key_as_blocked(
                    'elevenlabs',
                    api_key,
                    error_msg
                )

                # Retry с другим ключом
                return await self.generate_audio(
                    text, voice_id, output_path,
                    normalize_text=False,  # Уже нормализовали
                    remove_silence=remove_silence,
                    normalize_volume=normalize_volume
                )

        except Exception as e:
            print(f"   ❌ Ошибка: {e}")
            raise

    def _remove_long_silences(
        self,
        audio: AudioSegment,
        silence_thresh: int = -40,
        min_silence_len: int = 500,
        keep_silence: int = 200
    ) -> AudioSegment:
        """
        Обрезает длинные паузы в аудио

        Args:
            audio: Аудио сегмент
            silence_thresh: Порог тишины в dB (чем меньше, тем тише)
            min_silence_len: Минимальная длина паузы для обрезки (мс)
            keep_silence: Сколько тишины оставлять (мс)

        Returns:
            Обработанное аудио
        """

        # Находим не-тихие части
        nonsilent_ranges = detect_nonsilent(
            audio,
            min_silence_len=min_silence_len,
            silence_thresh=silence_thresh,
            seek_step=10
        )

        # Собираем аудио из не-тихих частей с короткими паузами
        chunks = []

        for i, (start, end) in enumerate(nonsilent_ranges):
            # Добавляем сам фрагмент
            chunk = audio[start:end]
            chunks.append(chunk)

            # Добавляем короткую паузу между фрагментами
            if i < len(nonsilent_ranges) - 1:
                silence = AudioSegment.silent(duration=keep_silence)
                chunks.append(silence)

        # Склеиваем всё
        if chunks:
            result = chunks[0]
            for chunk in chunks[1:]:
                result += chunk
            return result

        return audio

    def _normalize_volume(self, audio: AudioSegment, target_dBFS: float = -20.0) -> AudioSegment:
        """
        Нормализует громкость аудио

        Args:
            audio: Аудио сегмент
            target_dBFS: Целевая громкость в dBFS

        Returns:
            Нормализованное аудио
        """

        # Вычисляем разницу
        change_in_dBFS = target_dBFS - audio.dBFS

        # Применяем изменение
        return audio.apply_gain(change_in_dBFS)

    def get_voice_recommendations(self, niche: str) -> List[Dict]:
        """
        Рекомендует голоса для ниши

        Args:
            niche: Ниша (например, "psychology", "business", "tech")

        Returns:
            Список рекомендованных голосов
        """

        niche_lower = niche.lower()
        recommendations = []

        for voice_id, voice_config in self.voices.items():
            # Проверяем подходит ли голос
            for category in voice_config['best_for']:
                if category in niche_lower or niche_lower in category:
                    recommendations.append({
                        'voice_id': voice_id,
                        'name': voice_config['name'],
                        'description': voice_config['description'],
                        'style': voice_config['style'],
                        'gender': voice_config['gender']
                    })
                    break

        # Если ничего не нашли - даём универсальные
        if not recommendations:
            recommendations = [
                {
                    'voice_id': 'adam',
                    'name': 'Adam',
                    'description': 'Универсальный нарративный голос',
                    'style': 'narrative',
                    'gender': 'male'
                },
                {
                    'voice_id': 'rachel',
                    'name': 'Rachel',
                    'description': 'Универсальный женский голос',
                    'style': 'calm',
                    'gender': 'female'
                }
            ]

        return recommendations
