"""
ElevenLabs Manager - управление озвучкой и пулом API ключей
"""

import os
import json
import requests
import time
from typing import List, Dict, Optional

class ElevenLabsManager:
    """Менеджер для работы с ElevenLabs API"""

    def __init__(self, api_keys: List[str], proxy_config: Dict[str, str]):
        """
        Args:
            api_keys: список API ключей ElevenLabs
            proxy_config: {
                'host': 'pr-new.lunaproxy.com',
                'port': '12233',
                'username': 'user-...',
                'password': '...'
            }
        """
        self.api_keys = api_keys
        self.proxy_config = proxy_config
        self.current_key_index = 0

        # Статистика использования ключей
        self.keys_usage = {key: {'used_chars': 0, 'status': 'active'} for key in api_keys}

        # Кэш голосов
        self.voices_cache = None

        print(f"✅ ElevenLabsManager: {len(api_keys)} ключей загружено")

    def _get_proxy_dict(self) -> Dict[str, str]:
        """Получить прокси в формате requests"""
        username = self.proxy_config['username']
        password = self.proxy_config['password']
        host = self.proxy_config['host']
        port = self.proxy_config['port']

        proxy_url = f"http://{username}:{password}@{host}:{port}"

        return {
            'http': proxy_url,
            'https': proxy_url
        }

    def _get_active_key(self) -> Optional[str]:
        """
        Получить активный API ключ с доступным лимитом
        Автоматически переключается на следующий если лимит исчерпан
        """
        attempts = 0
        max_attempts = len(self.api_keys)

        while attempts < max_attempts:
            key = self.api_keys[self.current_key_index]
            usage = self.keys_usage[key]

            # Проверка статуса и лимита
            if usage['status'] == 'active' and usage['used_chars'] < 10000:
                return key

            # Переключиться на следующий ключ
            self.current_key_index = (self.current_key_index + 1) % len(self.api_keys)
            attempts += 1

        print("⚠️ Все ключи исчерпаны!")
        return None

    def _mark_key_used(self, key: str, chars_used: int):
        """Отметить использование символов"""
        if key in self.keys_usage:
            self.keys_usage[key]['used_chars'] += chars_used

            # Если превысили лимит
            if self.keys_usage[key]['used_chars'] >= 10000:
                print(f"⚠️ Ключ {key[:20]}... исчерпан (10k символов)")

    def _mark_key_blocked(self, key: str):
        """Отметить ключ как заблокированный"""
        if key in self.keys_usage:
            self.keys_usage[key]['status'] = 'blocked'
            print(f"❌ Ключ {key[:20]}... заблокирован")

    def get_voices(self, force_refresh: bool = False) -> List[Dict]:
        """
        Получить список всех доступных голосов

        Args:
            force_refresh: принудительно обновить кэш

        Returns:
            [
                {
                    'voice_id': '...',
                    'name': '...',
                    'gender': 'male' | 'female',
                    'labels': {...},
                    'preview_url': '...'
                },
                ...
            ]
        """
        # Вернуть из кэша если есть
        if self.voices_cache and not force_refresh:
            return self.voices_cache

        print("🔍 Получение списка голосов ElevenLabs...")

        key = self._get_active_key()
        if not key:
            return []

        try:
            proxies = self._get_proxy_dict()

            response = requests.get(
                'https://api.elevenlabs.io/v1/voices',
                headers={'xi-api-key': key},
                proxies=proxies,
                timeout=30
            )

            if response.status_code == 200:
                data = response.json()
                voices = data.get('voices', [])

                # Обработать голоса
                processed_voices = []

                for voice in voices:
                    # Классификация по гендеру
                    labels = voice.get('labels', {})
                    gender = labels.get('gender', 'unknown').lower()

                    # Если нет явного указания - попытаться определить по имени
                    if gender == 'unknown':
                        name_lower = voice.get('name', '').lower()
                        # Простая эвристика
                        if any(word in name_lower for word in ['male', 'man', 'boy', 'adam', 'josh']):
                            gender = 'male'
                        elif any(word in name_lower for word in ['female', 'woman', 'girl', 'rachel', 'bella']):
                            gender = 'female'

                    processed_voices.append({
                        'voice_id': voice.get('voice_id'),
                        'name': voice.get('name'),
                        'gender': gender,
                        'labels': labels,
                        'preview_url': voice.get('preview_url'),
                        'category': voice.get('category', 'generated')
                    })

                # Кэшировать
                self.voices_cache = processed_voices

                print(f"✅ Получено голосов: {len(processed_voices)}")
                print(f"   Мужских: {len([v for v in processed_voices if v['gender'] == 'male'])}")
                print(f"   Женских: {len([v for v in processed_voices if v['gender'] == 'female'])}")

                return processed_voices

            elif response.status_code == 401:
                print(f"❌ Ключ невалиден: {key[:20]}...")
                self._mark_key_blocked(key)
                return []

            else:
                print(f"⚠️ Ошибка API: {response.status_code}")
                return []

        except Exception as e:
            print(f"❌ Ошибка получения голосов: {e}")
            return []

    def generate_audio(self, text: str, voice_id: str, output_path: str) -> bool:
        """
        Генерация аудио

        Args:
            text: текст для озвучки
            voice_id: ID голоса
            output_path: путь сохранения MP3

        Returns:
            True если успешно
        """
        key = self._get_active_key()
        if not key:
            print("❌ Нет доступных ключей!")
            return False

        try:
            proxies = self._get_proxy_dict()

            # API запрос
            response = requests.post(
                f'https://api.elevenlabs.io/v1/text-to-speech/{voice_id}',
                headers={
                    'xi-api-key': key,
                    'Content-Type': 'application/json'
                },
                json={
                    'text': text,
                    'model_id': 'eleven_monolingual_v1',
                    'voice_settings': {
                        'stability': 0.5,
                        'similarity_boost': 0.75
                    }
                },
                proxies=proxies,
                timeout=60
            )

            if response.status_code == 200:
                # Сохранить аудио
                os.makedirs(os.path.dirname(output_path), exist_ok=True)

                with open(output_path, 'wb') as f:
                    f.write(response.content)

                # Отметить использование
                self._mark_key_used(key, len(text))

                return True

            elif response.status_code == 401:
                self._mark_key_blocked(key)
                print(f"❌ Ключ заблокирован: {key[:20]}...")
                return False

            else:
                print(f"⚠️ Ошибка генерации: {response.status_code}")
                return False

        except Exception as e:
            print(f"❌ Ошибка: {e}")
            return False

    def get_usage_stats(self) -> Dict:
        """Получить статистику использования ключей"""
        active = len([k for k, v in self.keys_usage.items() if v['status'] == 'active'])
        blocked = len([k for k, v in self.keys_usage.items() if v['status'] == 'blocked'])
        total_used = sum(v['used_chars'] for v in self.keys_usage.values())

        return {
            'total_keys': len(self.api_keys),
            'active_keys': active,
            'blocked_keys': blocked,
            'total_chars_used': total_used,
            'total_chars_available': active * 10000
        }


# === ГЛОБАЛЬНЫЙ ИНСТАНС ===

_elevenlabs_manager = None

def get_elevenlabs_manager() -> ElevenLabsManager:
    """Получить глобальный инстанс менеджера"""
    global _elevenlabs_manager

    if _elevenlabs_manager is None:
        # Загрузить ключи из файла
        keys_file = os.path.join(os.path.dirname(__file__), '..', 'config', 'elevenlabs_keys.txt')

        if not os.path.exists(keys_file):
            raise Exception(f"Файл с ключами не найден: {keys_file}")

        with open(keys_file, 'r') as f:
            keys = [line.strip() for line in f if line.strip() and line.strip().startswith('sk_')]

        # Конфигурация прокси
        proxy_config = {
            'host': 'pr-new.lunaproxy.com',
            'port': '12233',
            'username': 'user-4tu6e3cvvga6-sessid-allda1xw9twr8swhpte-sesstime-90',
            'password': 'GaSf8kAK2qM1g'
        }

        _elevenlabs_manager = ElevenLabsManager(keys, proxy_config)

    return _elevenlabs_manager
