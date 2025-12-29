#!/usr/bin/env python3
"""
Централизованная система управления API ключами с автоматической ротацией

БЕЗОПАСНОСТЬ:
- Ключи НЕ хардкодятся в коде
- Загружаются из .env или .keys_secure.json
- Поддержка автоматической ротации
- Статистика использования
"""

import os
import json
import hashlib
from typing import Optional, List, Dict
from datetime import datetime
from dotenv import load_dotenv


class APIKeyManager:
    """Менеджер API ключей с автоматической ротацией и мониторингом"""

    def __init__(self, cache_file: str = ".api_keys_cache.json", keys_file: str = ".keys_secure.json"):
        """
        Инициализация менеджера ключей

        Args:
            cache_file: Файл для кэша использования
            keys_file: Файл с ключами (опционально, не коммитится в git)
        """
        load_dotenv()

        self.cache_file = cache_file
        self.keys_file = keys_file
        self.cache = self._load_cache()

        # Загружаем ключи из разных источников
        self._load_keys()

        print(f"🔑 APIKeyManager инициализирован")
        print(f"   Gemini ключей: {len(self.gemini_keys)}")
        print(f"   Hugging Face ключей: {len(self.hf_keys)}")
        print(f"   YouTube ключей: {len(self.youtube_keys)}")
        print(f"   Grok ключей: {len(self.grok_keys)}")

    def _load_keys(self):
        """Загружает ключи из .env и .keys_secure.json"""

        # Google Gemini ключи
        self.gemini_keys = []
        for i in range(1, 11):  # Поддержка до 10 ключей
            key = os.getenv(f'GOOGLE_API_KEY_{i}')
            if key and key != 'your_google_api_key_here':
                self.gemini_keys.append(key)

        # Если нет пронумерованных, пробуем старый формат
        if not self.gemini_keys:
            key = os.getenv('GOOGLE_API_KEY')
            if key and key != 'your_google_api_key_here':
                self.gemini_keys.append(key)

        # Hugging Face ключи
        self.hf_keys = []
        # Из .env (пронумерованные)
        for i in range(1, 201):  # Поддержка до 200 ключей
            key = os.getenv(f'HF_API_KEY_{i}')
            if key and key != 'your_hf_key_here':
                self.hf_keys.append(key)

        # Или из списка в .env (формат: key1,key2,key3)
        if not self.hf_keys:
            keys_list = os.getenv('HF_KEYS_LIST', '')
            if keys_list:
                self.hf_keys = [k.strip() for k in keys_list.split(',') if k.strip()]

        # YouTube Data API ключи
        self.youtube_keys = []
        for i in range(1, 11):  # Поддержка до 10 ключей
            key = os.getenv(f'YOUTUBE_API_KEY_{i}')
            if key and key != 'your_youtube_api_key_here':
                self.youtube_keys.append(key)

        # Старый формат
        if not self.youtube_keys:
            key = os.getenv('YOUTUBE_API_KEY')
            if key and key != 'your_youtube_api_key_here':
                self.youtube_keys.append(key)

        # Grok ключи (загружаются из GROK_KEYS_LIST как раньше)
        self.grok_keys = []
        keys_env = os.getenv('GROK_KEYS_LIST', '')
        if keys_env:
            self.grok_keys = [key.strip() for key in keys_env.split(',') if key.strip()]

        # Пробуем загрузить из .keys_secure.json если есть
        if os.path.exists(self.keys_file):
            try:
                with open(self.keys_file, 'r') as f:
                    secure_keys = json.load(f)

                # Добавляем ключи из файла если их нет
                if 'gemini' in secure_keys:
                    self.gemini_keys.extend([k for k in secure_keys['gemini'] if k not in self.gemini_keys])

                if 'huggingface' in secure_keys:
                    self.hf_keys.extend([k for k in secure_keys['huggingface'] if k not in self.hf_keys])

                if 'youtube' in secure_keys:
                    self.youtube_keys.extend([k for k in secure_keys['youtube'] if k not in self.youtube_keys])

                if 'grok' in secure_keys:
                    self.grok_keys.extend([k for k in secure_keys['grok'] if k not in self.grok_keys])

            except Exception as e:
                print(f"⚠️  Ошибка загрузки {self.keys_file}: {e}")

    def _load_cache(self) -> Dict:
        """Загружает кэш использования ключей"""
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'r') as f:
                    return json.load(f)
            except:
                return {}
        return {}

    def _save_cache(self):
        """Сохраняет кэш использования"""
        try:
            with open(self.cache_file, 'w') as f:
                json.dump(self.cache, f, indent=2)
        except Exception as e:
            print(f"⚠️  Ошибка сохранения кэша: {e}")

    def get_gemini_key(self) -> str:
        """Возвращает Gemini ключ с наименьшим использованием"""
        if not self.gemini_keys:
            raise ValueError(
                "Нет доступных Google Gemini ключей!\n"
                "Добавьте в .env: GOOGLE_API_KEY_1=your_key"
            )
        return self._rotate_key('gemini', self.gemini_keys)

    def get_hf_key(self) -> str:
        """Возвращает Hugging Face ключ с наименьшим использованием"""
        if not self.hf_keys:
            raise ValueError(
                "Нет доступных Hugging Face ключей!\n"
                "Добавьте в .env: HF_KEYS_LIST=key1,key2,key3 или HF_API_KEY_1=key1"
            )
        return self._rotate_key('huggingface', self.hf_keys)

    def get_youtube_key(self) -> str:
        """Возвращает YouTube API ключ с наименьшим использованием"""
        if not self.youtube_keys:
            raise ValueError(
                "Нет доступных YouTube API ключей!\n"
                "Добавьте в .env: YOUTUBE_API_KEY_1=your_key"
            )
        return self._rotate_key('youtube', self.youtube_keys)

    def get_grok_key(self) -> Optional[str]:
        """Возвращает Grok ключ с наименьшим использованием (если есть)"""
        if not self.grok_keys:
            return None
        return self._rotate_key('grok', self.grok_keys)

    def _rotate_key(self, service: str, keys: List[str]) -> str:
        """
        Ротация ключей на основе использования

        Args:
            service: Имя сервиса (gemini, huggingface, youtube, grok)
            keys: Список доступных ключей

        Returns:
            Ключ с наименьшим использованием
        """
        if service not in self.cache:
            self.cache[service] = {}

        # Находим ключ с наименьшим использованием
        min_usage = float('inf')
        selected_key = keys[0]

        for key in keys:
            # Хэшируем ключ для анонимности в кэше
            key_hash = hashlib.md5(key.encode()).hexdigest()[:8]
            usage = self.cache[service].get(key_hash, 0)

            if usage < min_usage:
                min_usage = usage
                selected_key = key

        # Увеличиваем счётчик использования
        key_hash = hashlib.md5(selected_key.encode()).hexdigest()[:8]
        self.cache[service][key_hash] = self.cache[service].get(key_hash, 0) + 1
        self._save_cache()

        return selected_key

    def get_stats(self) -> Dict:
        """Статистика использования ключей"""
        stats = {
            'gemini': {
                'total_keys': len(self.gemini_keys),
                'requests': sum(self.cache.get('gemini', {}).values()),
                'available': len(self.gemini_keys) > 0
            },
            'huggingface': {
                'total_keys': len(self.hf_keys),
                'requests': sum(self.cache.get('huggingface', {}).values()),
                'available': len(self.hf_keys) > 0
            },
            'youtube': {
                'total_keys': len(self.youtube_keys),
                'requests': sum(self.cache.get('youtube', {}).values()),
                'available': len(self.youtube_keys) > 0
            },
            'grok': {
                'total_keys': len(self.grok_keys),
                'requests': sum(self.cache.get('grok', {}).values()),
                'available': len(self.grok_keys) > 0
            }
        }
        return stats

    def reset_stats(self):
        """Сбрасывает статистику использования"""
        self.cache = {}
        self._save_cache()
        print("✅ Статистика использования сброшена")

    def print_stats(self):
        """Выводит статистику в консоль"""
        stats = self.get_stats()

        print("\n📊 СТАТИСТИКА API КЛЮЧЕЙ:")
        print("═" * 60)

        for service, data in stats.items():
            status = "✅" if data['available'] else "❌"
            print(f"{status} {service.upper()}:")
            print(f"   Ключей: {data['total_keys']}")
            print(f"   Запросов: {data['requests']}")
            print()

        print("═" * 60)
