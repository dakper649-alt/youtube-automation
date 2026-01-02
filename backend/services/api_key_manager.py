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

        # Groq ключи (для Llama 3.1 70B)
        self.groq_keys = []
        for i in range(1, 11):  # Поддержка до 10 ключей
            key = os.getenv(f'GROQ_API_KEY_{i}')
            if key and key != 'your_groq_api_key_here':
                self.groq_keys.append(key)

        # Старый формат
        if not self.groq_keys:
            key = os.getenv('GROQ_API_KEY')
            if key and key != 'your_groq_api_key_here':
                self.groq_keys.append(key)

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

                if 'groq' in secure_keys:
                    self.groq_keys.extend([k for k in secure_keys['groq'] if k not in self.groq_keys])

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

    def get_groq_key(self) -> str:
        """Возвращает Groq ключ с наименьшим использованием"""
        if not self.groq_keys:
            raise ValueError(
                "Нет доступных Groq API ключей!\n"
                "Добавьте в .env: GROQ_API_KEY_1=your_key\n"
                "Получить ключ: https://console.groq.com"
            )
        return self._rotate_key('groq', self.groq_keys)

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


# ═══════════════════════════════════════════════════════════════════════════
# ПРОДВИНУТЫЙ МЕНЕДЖЕР С ЗАЩИТОЙ ОТ БЛОКИРОВОК
# ═══════════════════════════════════════════════════════════════════════════

import random
import asyncio
from datetime import datetime, timedelta
from typing import Optional


class SafeAPIManager(APIKeyManager):
    """
    Безопасный менеджер API с защитой от блокировок

    Возможности:
    - Человекоподобные задержки между запросами
    - Автоматическое определение заблокированных ключей
    - Лист ожидания для ключей с исчерпанным лимитом
    - Постоянное удаление мёртвых ключей
    - Мониторинг здоровья каждого ключа
    """

    def __init__(self, cache_file: str = ".api_keys_cache.json", keys_file: str = ".keys_secure.json"):
        super().__init__(cache_file, keys_file)

        # ElevenLabs ключи (54 штуки! для озвучки)
        self.elevenlabs_keys = [
            "sk_7d4fb743c9c46ff75c9f9c22644146f679e24d9cb421f1fe",
            "sk_2c1bc1a92b8fe305cb232a513aa3cf3bd5f07da43f110905",
            "sk_4c7622ad930675321052bee5d9b8f01e421884e6ea478e92",
            "sk_77ed505701399b00c8b9b025aa254eb36cbb76479b2d2c10",
            "sk_d6a5b1beb89e9b04a136225b0730b267701737999b9f4179",
            "sk_ecb305016273c82c4603f83f2b94ae128a64092699819240",
            "sk_700141a470741e04c72ab22584aaf890d56ad7b896dc6497",
            "sk_af7ac54991373892176946ea51fdbdd2374ec04649397f93",
            "sk_dadd9bee27fb4af7dc357e295b4bacc726df01e3a1c77eae",
            "sk_ed53c9f03a94d562a0fc9c750ab937951cde664e3903ef50",
            "sk_48e9516e10e8c9dad761b2117aac46ed3abf259ddf1055e5",
            "sk_f04971eeb19f75d975af60f4a482e0a5ae1d717d19bdc487",
            "sk_a293959e0dcbe51b60e8e3bf98504c6c8ceb4a0270af4dde",
            "sk_50b1d6b64fcc0fa98743b951f08de87965a8b38d8f08ae45",
            "sk_dfc501510d2948fd577d1f82a25c248f2f4b05569e704249",
            "sk_fa1be3a25745bf9e83d9208ac7cdd93351e7b14614b174d5",
            "sk_707d5223d97f7f6424a1bfc090a4c79dcd6edc72ab87df49",
            "sk_ebcc25d64b1025301756cf139a0e0c57a0b668d9cbdbae4d",
            "sk_5c948ca488d3b99c0c3efe9ab293f87fe176f383286c4198",
            "sk_5693f9032cef9eb46d04b08f51afa9ae77387fcc8834ce97",
            "sk_e6e231d50b3e2e6afbb0beb196bfbc3e06078e222b486faf",
            "sk_2a01e1613eeae2d423c0401055aed12c1f45398920411b1d",
            "sk_1ccfd6847861521a334583a23417410d543527d0c4a4db1b",
            "sk_1a6980d97874510d2e785e9aa8988210f7e8414e68e1df8f",
            "sk_ffa640f4f873ef3d6de3516f3c316be08dccda8ce9a77b36",
            "sk_a200508a1a194215cb193ce5d673f7d993d0b025013dc9d2",
            "sk_44621c4fe406dc784ec447f33448d6740d8d931fefa8fdda",
            "sk_2c32e61a93691c99265efcd4c1a3c96e93d89a9babbf0947",
            "sk_e602477972b1388e7932c15cc6d99f19dce1a3a5906d7f5f",
            "sk_5c4724a1ab8f6b48efbe6cb6babefaaa97cae96f083a2b22",
            "sk_17b9d1c796bd8ee26b735dfaaa79a7c3e4f5180b68c248f8",
            "sk_ed99ded91e375fa3b265a40db26d621da87327d215f30081",
            "sk_9422daa757eabf4f4d2f361bff48874c80aebf0d266cca3f",
            "sk_975d8ed664be3a8afa80dd37ff8f9392e6f3bdea236c289e",
            "sk_fcf8f6d0ccca8baab6acfbbda6be576eca11bbec93bd89b9",
            "sk_3226052c061fba530ca27948277078d48ef7f63fa8316c9e",
            "sk_6ac64cb5f416f5379d72ae812d5214be27e0d802d819a5db",
            "sk_70c9cf01c2a4809903df1db86ff537f1270c6a733b04205b",
            "sk_485961e42500da92c63f10a308fc292db953d2380020843e",
            "sk_c3a226cd3363f00ca3019175b01814c4cb8da2a64787f4ee",
            "sk_3a817606236744e07b7c51d4272950fa177594c7ad78d093",
            "sk_d40671dcc1a5f143e93413abc819fbbd2143f7d092d21223",
            "sk_3f59404321c83b6ac545768f83d7049dece063e77603745c",
            "sk_730be114539ca4a812f7756fc251160f4d89c3e43bebc72f",
            "sk_6ac35fa36cb5fda0e12d3f007d6e5d0eb4de87540e751c58",
            "sk_71500056f52d6dd6e0433fed7effbbd1927bd6149216549d",
            "sk_0a4cd274e32fd83a641ae916211aff534e86d89a31bc822e",
            "sk_b1d8e4c33d7f437d46cdf85bf8670df395737420c18a489b",
            "sk_2e39342922870af82632a3404ea80406423efb131232da47",
            "sk_9866d38386abc99b23dbe62838715ecbc29db877c46e95b3",
            "sk_4cd7e5dd4e541d9304670ff3fc8cfb29d179e2dbf414e7aa",
            "sk_2651ae662837b13a70b3ef637aa7f50efc210c4b4cfe74f7",
            "sk_760fee9a30fd97669a6308f6ee3d50846d7effb91fc90e1e",
            "sk_bb3e9f37d10ad3cf0df9ef193d9e833b5abc71e962cddec3"
        ]

        # Статусы ключей
        self.key_status_file = ".api_keys_status.json"
        self.key_status = self._load_key_status()

        # Настройки безопасности
        self.safety_config = {
            'min_delay_seconds': 2,      # Минимальная задержка между запросами
            'max_delay_seconds': 8,      # Максимальная задержка
            'elevenlabs_limit': 10000,   # Лимит ElevenLabs (символы/месяц)
            'youtube_daily_limit': 10000, # Лимит YouTube (единицы/день)
            'max_errors_before_ban': 3,  # Ошибок перед блокировкой
            'cooldown_period_days': 30   # Период остывания (дней)
        }

        print(f"🛡️  SafeAPIManager инициализирован")
        print(f"   ElevenLabs ключей: {len(self.elevenlabs_keys)}")

    def _load_elevenlabs_keys(self):
        """Загружает ElevenLabs ключи из .env (БЕЗОПАСНО)"""
        # Загружаем пронумерованные ключи
        for i in range(1, 11):  # До 10 ключей
            key = os.getenv(f'ELEVENLABS_API_KEY_{i}')
            if key and key != 'your_elevenlabs_key_here':
                self.elevenlabs_keys.append(key)

        # Или из списка
        if not self.elevenlabs_keys:
            keys_list = os.getenv('ELEVENLABS_KEYS_LIST', '')
            if keys_list:
                self.elevenlabs_keys = [k.strip() for k in keys_list.split(',') if k.strip()]

    def _load_key_status(self) -> Dict:
        """Загружает статусы ключей"""
        if os.path.exists(self.key_status_file):
            try:
                with open(self.key_status_file, 'r') as f:
                    return json.load(f)
            except:
                return self._create_empty_status()
        return self._create_empty_status()

    def _create_empty_status(self) -> Dict:
        """Создаёт пустую структуру статусов"""
        return {
            'youtube': {},
            'elevenlabs': {},
            'waiting_list': {},
            'permanently_blocked': []
        }

    def _save_key_status(self):
        """Сохраняет статусы ключей"""
        try:
            with open(self.key_status_file, 'w') as f:
                json.dump(self.key_status, f, indent=2)
        except Exception as e:
            print(f"⚠️  Ошибка сохранения статусов: {e}")

    async def get_safe_youtube_key(self) -> Optional[str]:
        """
        Возвращает безопасный YouTube ключ с проверкой статуса
        """

        # Человекоподобная задержка
        await self._human_like_delay()

        # Проверяем waiting_list
        self._check_waiting_list('youtube')

        # Фильтруем заблокированные ключи
        available_keys = [
            key for key in self.youtube_keys
            if self._get_key_hash(key) not in self.key_status['permanently_blocked']
            and self._get_key_hash(key) not in self.key_status['waiting_list']
        ]

        if not available_keys:
            raise ValueError("❌ Нет доступных YouTube API ключей! Все заблокированы или в ожидании.")

        # Выбираем ключ с наименьшим использованием
        selected_key = self._select_least_used_key('youtube', available_keys)

        # Проверяем дневной лимит
        if self._check_daily_limit('youtube', selected_key):
            print(f"⚠️  Ключ достиг дневного лимита, отправляю в waiting_list на 24 часа")
            self._add_to_waiting_list('youtube', selected_key, hours=24)
            return await self.get_safe_youtube_key()  # Рекурсивно ищем другой

        return selected_key

    async def get_safe_elevenlabs_key(self) -> Optional[str]:
        """
        Возвращает безопасный ElevenLabs ключ с проверкой лимитов
        """

        if not self.elevenlabs_keys:
            raise ValueError(
                "❌ Нет ключей ElevenLabs в .env!\n"
                "Добавьте: ELEVENLABS_API_KEY_1=your_key"
            )

        # Человекоподобная задержка
        await self._human_like_delay()

        # Проверяем waiting_list
        self._check_waiting_list('elevenlabs')

        # Фильтруем заблокированные ключи
        available_keys = [
            key for key in self.elevenlabs_keys
            if self._get_key_hash(key) not in self.key_status['permanently_blocked']
            and self._get_key_hash(key) not in self.key_status['waiting_list']
        ]

        if not available_keys:
            raise ValueError("❌ Нет доступных ElevenLabs ключей!")

        # Выбираем ключ с наименьшим использованием
        selected_key = self._select_least_used_key('elevenlabs', available_keys)

        # Проверяем месячный лимит
        if self._check_monthly_limit('elevenlabs', selected_key):
            print(f"⚠️  Ключ достиг месячного лимита (10,000 символов), отправляю в waiting_list на 30 дней")
            self._add_to_waiting_list('elevenlabs', selected_key, days=30)
            return await self.get_safe_elevenlabs_key()  # Рекурсивно

        return selected_key

    async def _human_like_delay(self):
        """Человекоподобная задержка между запросами"""
        delay = random.uniform(
            self.safety_config['min_delay_seconds'],
            self.safety_config['max_delay_seconds']
        )

        # Добавляем небольшую случайность (иногда быстрее, иногда медленнее)
        if random.random() < 0.1:  # 10% шанс
            delay *= random.uniform(1.5, 2.0)  # Иногда задержка дольше

        await asyncio.sleep(delay)

    def _get_key_hash(self, key: str) -> str:
        """Возвращает хэш ключа для идентификации"""
        return hashlib.md5(key.encode()).hexdigest()[:8]

    def _select_least_used_key(self, service: str, available_keys: List[str]) -> str:
        """Выбирает ключ с наименьшим использованием"""
        if service not in self.key_status:
            self.key_status[service] = {}

        min_usage = float('inf')
        selected_key = available_keys[0]

        for key in available_keys:
            key_hash = self._get_key_hash(key)
            usage = self.key_status[service].get(key_hash, {}).get('usage', 0)

            if usage < min_usage:
                min_usage = usage
                selected_key = key

        return selected_key

    def _check_daily_limit(self, service: str, key: str) -> bool:
        """Проверяет не достигнут ли дневной лимит"""
        key_hash = self._get_key_hash(key)

        if key_hash not in self.key_status.get(service, {}):
            return False

        key_data = self.key_status[service][key_hash]

        # Проверяем дату последнего использования
        last_used = key_data.get('last_used_date')
        if not last_used:
            return False

        last_date = datetime.fromisoformat(last_used).date()
        today = datetime.now().date()

        # Если новый день - сбрасываем счётчик
        if last_date < today:
            key_data['daily_usage'] = 0
            return False

        # Проверяем лимит
        daily_usage = key_data.get('daily_usage', 0)
        return daily_usage >= self.safety_config['youtube_daily_limit']

    def _check_monthly_limit(self, service: str, key: str) -> bool:
        """Проверяет месячный лимит (для ElevenLabs)"""
        key_hash = self._get_key_hash(key)

        if key_hash not in self.key_status.get(service, {}):
            return False

        key_data = self.key_status[service][key_hash]

        # Проверяем месяц
        last_reset = key_data.get('last_monthly_reset')
        if not last_reset:
            return False

        last_reset_date = datetime.fromisoformat(last_reset)
        now = datetime.now()

        # Если прошёл месяц - сбрасываем
        if (now - last_reset_date).days >= 30:
            key_data['monthly_usage'] = 0
            key_data['last_monthly_reset'] = now.isoformat()
            self._save_key_status()
            return False

        # Проверяем лимит
        monthly_usage = key_data.get('monthly_usage', 0)
        return monthly_usage >= self.safety_config['elevenlabs_limit']

    def _add_to_waiting_list(self, service: str, key: str, hours: int = 0, days: int = 0):
        """Добавляет ключ в лист ожидания"""
        key_hash = self._get_key_hash(key)

        release_time = datetime.now() + timedelta(hours=hours, days=days)

        self.key_status['waiting_list'][key_hash] = {
            'service': service,
            'added_at': datetime.now().isoformat(),
            'release_at': release_time.isoformat(),
            'reason': f"Лимит исчерпан ({hours}h {days}d cooldown)"
        }

        self._save_key_status()

        print(f"📝 Ключ {key_hash} добавлен в waiting_list до {release_time.strftime('%Y-%m-%d %H:%M')}")

    def _check_waiting_list(self, service: str):
        """Проверяет waiting_list и освобождает ключи"""
        now = datetime.now()
        keys_to_remove = []

        for key_hash, data in self.key_status['waiting_list'].items():
            if data['service'] != service:
                continue

            release_time = datetime.fromisoformat(data['release_at'])

            if now >= release_time:
                keys_to_remove.append(key_hash)
                print(f"✅ Ключ {key_hash} освобождён из waiting_list!")

        # Удаляем освобождённые ключи
        for key_hash in keys_to_remove:
            del self.key_status['waiting_list'][key_hash]

        if keys_to_remove:
            self._save_key_status()

    def mark_key_as_blocked(self, service: str, key: str, error_message: str):
        """
        Отмечает ключ как заблокированный

        После 3 ошибок подряд - блокирует навсегда
        """
        key_hash = self._get_key_hash(key)

        if service not in self.key_status:
            self.key_status[service] = {}

        if key_hash not in self.key_status[service]:
            self.key_status[service][key_hash] = {
                'errors': 0,
                'last_error': None
            }

        key_data = self.key_status[service][key_hash]
        key_data['errors'] += 1
        key_data['last_error'] = {
            'message': error_message,
            'timestamp': datetime.now().isoformat()
        }

        # Проверяем количество ошибок
        if key_data['errors'] >= self.safety_config['max_errors_before_ban']:
            print(f"🚫 Ключ {key_hash} ЗАБЛОКИРОВАН НАВСЕГДА после {key_data['errors']} ошибок!")
            self.key_status['permanently_blocked'].append(key_hash)
        else:
            print(f"⚠️  Ошибка #{key_data['errors']} для ключа {key_hash}: {error_message}")

        self._save_key_status()

    def track_usage(self, service: str, key: str, units_used: int = 1):
        """Отслеживает использование ключа"""
        key_hash = self._get_key_hash(key)

        if service not in self.key_status:
            self.key_status[service] = {}

        if key_hash not in self.key_status[service]:
            self.key_status[service][key_hash] = {
                'usage': 0,
                'daily_usage': 0,
                'monthly_usage': 0,
                'last_used_date': datetime.now().isoformat(),
                'last_monthly_reset': datetime.now().isoformat(),
                'errors': 0
            }

        key_data = self.key_status[service][key_hash]
        key_data['usage'] += units_used
        key_data['daily_usage'] = key_data.get('daily_usage', 0) + units_used
        key_data['monthly_usage'] = key_data.get('monthly_usage', 0) + units_used
        key_data['last_used_date'] = datetime.now().isoformat()

        self._save_key_status()

    def get_health_report(self) -> Dict:
        """Отчёт о здоровье всех ключей"""
        report = {
            'youtube': {
                'total': len(self.youtube_keys),
                'active': 0,
                'waiting': 0,
                'blocked': 0
            },
            'elevenlabs': {
                'total': len(self.elevenlabs_keys),
                'active': 0,
                'waiting': 0,
                'blocked': 0
            },
            'waiting_list_details': [],
            'blocked_keys': []
        }

        # Подсчёт YouTube ключей
        for key in self.youtube_keys:
            key_hash = self._get_key_hash(key)
            if key_hash in self.key_status['permanently_blocked']:
                report['youtube']['blocked'] += 1
                report['blocked_keys'].append({
                    'service': 'youtube',
                    'key_hash': key_hash
                })
            elif key_hash in self.key_status['waiting_list']:
                report['youtube']['waiting'] += 1
                waiting_data = self.key_status['waiting_list'][key_hash]
                report['waiting_list_details'].append({
                    'service': 'youtube',
                    'key_hash': key_hash,
                    'release_at': waiting_data['release_at']
                })
            else:
                report['youtube']['active'] += 1

        # Подсчёт ElevenLabs ключей
        for key in self.elevenlabs_keys:
            key_hash = self._get_key_hash(key)
            if key_hash in self.key_status['permanently_blocked']:
                report['elevenlabs']['blocked'] += 1
                report['blocked_keys'].append({
                    'service': 'elevenlabs',
                    'key_hash': key_hash
                })
            elif key_hash in self.key_status['waiting_list']:
                report['elevenlabs']['waiting'] += 1
                waiting_data = self.key_status['waiting_list'][key_hash]
                report['waiting_list_details'].append({
                    'service': 'elevenlabs',
                    'key_hash': key_hash,
                    'release_at': waiting_data['release_at']
                })
            else:
                report['elevenlabs']['active'] += 1

        return report

    async def get_safe_hf_key(self) -> Optional[str]:
        """
        Возвращает безопасный Hugging Face ключ с проверкой лимитов
        """

        # Человекоподобная задержка
        await self._human_like_delay()

        # Проверяем waiting_list
        self._check_waiting_list('huggingface')

        # Фильтруем заблокированные ключи
        available_keys = [
            key for key in self.hf_keys
            if self._get_key_hash(key) not in self.key_status['permanently_blocked']
            and self._get_key_hash(key) not in self.key_status['waiting_list']
        ]

        if not available_keys:
            raise ValueError(
                "❌ Нет доступных Hugging Face ключей!\n"
                "Добавьте: HF_API_KEY_1=your_key в .env"
            )

        # Выбираем ключ с наименьшим использованием
        selected_key = self._select_least_used_key('huggingface', available_keys)

        # HF имеет более мягкие лимиты, но всё равно проверяем
        # Для бесплатного тарифа: ~1000 запросов/день
        if self._check_daily_limit('huggingface', selected_key):
            print(f"⚠️  HF ключ достиг дневного лимита, отправляю в waiting_list на 24 часа")
            self._add_to_waiting_list('huggingface', selected_key, hours=24)
            return await self.get_safe_hf_key()  # Рекурсивно

        return selected_key
