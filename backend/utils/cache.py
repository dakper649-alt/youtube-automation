"""
Модуль для кэширования данных YouTube API

Использует SQLite для хранения результатов с TTL (time-to-live)
Автоматически очищает устаревшие записи
"""

import sqlite3
import json
import time
from typing import Any, Optional
from pathlib import Path
import hashlib


class YouTubeCache:
    """Кэш для YouTube API данных с поддержкой TTL"""

    def __init__(self, db_path: str = "youtube_cache.db"):
        """
        Инициализация кэша

        Args:
            db_path: Путь к файлу базы данных SQLite
        """
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """Создание таблиц базы данных"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS cache (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL,
                    expires_at INTEGER NOT NULL,
                    created_at INTEGER NOT NULL
                )
            """)
            # Индекс для быстрой очистки устаревших записей
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_expires_at
                ON cache(expires_at)
            """)
            conn.commit()

    def _generate_key(self, prefix: str, **kwargs) -> str:
        """
        Генерация ключа кэша

        Args:
            prefix: Префикс ключа (например, 'channel_info')
            **kwargs: Параметры для генерации уникального ключа

        Returns:
            str: Хэш ключа
        """
        # Создаём строку из всех параметров
        params_str = json.dumps(kwargs, sort_keys=True)
        # Генерируем хэш
        key_hash = hashlib.md5(params_str.encode()).hexdigest()
        return f"{prefix}:{key_hash}"

    def get(self, key: str) -> Optional[Any]:
        """
        Получение значения из кэша

        Args:
            key: Ключ

        Returns:
            Значение или None если не найдено/устарело
        """
        current_time = int(time.time())

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT value FROM cache WHERE key = ? AND expires_at > ?",
                (key, current_time)
            )
            row = cursor.fetchone()

            if row:
                return json.loads(row[0])

        return None

    def set(self, key: str, value: Any, ttl: int = 3600):
        """
        Сохранение значения в кэш

        Args:
            key: Ключ
            value: Значение (должно быть JSON-сериализуемым)
            ttl: Время жизни в секундах (по умолчанию 1 час)
        """
        current_time = int(time.time())
        expires_at = current_time + ttl

        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO cache (key, value, expires_at, created_at)
                VALUES (?, ?, ?, ?)
                """,
                (key, json.dumps(value), expires_at, current_time)
            )
            conn.commit()

    def delete(self, key: str):
        """Удаление записи из кэша"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM cache WHERE key = ?", (key,))
            conn.commit()

    def clear_expired(self):
        """Очистка устаревших записей"""
        current_time = int(time.time())

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "DELETE FROM cache WHERE expires_at <= ?",
                (current_time,)
            )
            deleted_count = cursor.rowcount
            conn.commit()

        return deleted_count

    def clear_all(self):
        """Полная очистка кэша"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM cache")
            conn.commit()

    def get_stats(self) -> dict:
        """
        Получение статистики кэша

        Returns:
            dict: Статистика
        """
        current_time = int(time.time())

        with sqlite3.connect(self.db_path) as conn:
            # Всего записей
            total = conn.execute("SELECT COUNT(*) FROM cache").fetchone()[0]

            # Актуальных записей
            valid = conn.execute(
                "SELECT COUNT(*) FROM cache WHERE expires_at > ?",
                (current_time,)
            ).fetchone()[0]

            # Устаревших записей
            expired = total - valid

            # Размер БД в байтах
            db_size = Path(self.db_path).stat().st_size if Path(self.db_path).exists() else 0

        return {
            'total_entries': total,
            'valid_entries': valid,
            'expired_entries': expired,
            'db_size_mb': round(db_size / 1024 / 1024, 2)
        }


class QuotaTracker:
    """Трекинг использования YouTube API квоты"""

    def __init__(self, db_path: str = "youtube_quota.db", daily_limit: int = 10000):
        """
        Инициализация трекера квоты

        Args:
            db_path: Путь к файлу базы данных
            daily_limit: Дневной лимит единиц (по умолчанию 10,000)
        """
        self.db_path = db_path
        self.daily_limit = daily_limit
        self._init_db()

    def _init_db(self):
        """Создание таблиц"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS quota_usage (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    operation TEXT NOT NULL,
                    cost INTEGER NOT NULL,
                    timestamp INTEGER NOT NULL,
                    date TEXT NOT NULL
                )
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_date
                ON quota_usage(date)
            """)
            conn.commit()

    def _get_current_date(self) -> str:
        """Получение текущей даты в формате YYYY-MM-DD"""
        from datetime import datetime
        return datetime.now().strftime('%Y-%m-%d')

    def track(self, operation: str, cost: int):
        """
        Запись использования квоты

        Args:
            operation: Название операции
            cost: Стоимость в единицах API
        """
        current_time = int(time.time())
        current_date = self._get_current_date()

        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT INTO quota_usage (operation, cost, timestamp, date)
                VALUES (?, ?, ?, ?)
                """,
                (operation, cost, current_time, current_date)
            )
            conn.commit()

    def get_today_usage(self) -> int:
        """Получение использованной квоты за сегодня"""
        current_date = self._get_current_date()

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT COALESCE(SUM(cost), 0) FROM quota_usage WHERE date = ?",
                (current_date,)
            )
            return cursor.fetchone()[0]

    def get_remaining(self) -> int:
        """Получение оставшейся квоты"""
        used = self.get_today_usage()
        return max(0, self.daily_limit - used)

    def get_usage_stats(self) -> dict:
        """
        Детальная статистика использования

        Returns:
            dict: Статистика
        """
        current_date = self._get_current_date()
        used_today = self.get_today_usage()
        remaining = self.get_remaining()

        with sqlite3.connect(self.db_path) as conn:
            # Топ операций за сегодня
            cursor = conn.execute("""
                SELECT operation, SUM(cost) as total_cost, COUNT(*) as count
                FROM quota_usage
                WHERE date = ?
                GROUP BY operation
                ORDER BY total_cost DESC
                LIMIT 10
            """, (current_date,))

            top_operations = [
                {
                    'operation': row[0],
                    'total_cost': row[1],
                    'count': row[2]
                }
                for row in cursor.fetchall()
            ]

        percentage_used = (used_today / self.daily_limit * 100) if self.daily_limit > 0 else 0

        return {
            'date': current_date,
            'used_today': used_today,
            'remaining': remaining,
            'daily_limit': self.daily_limit,
            'percentage_used': round(percentage_used, 2),
            'top_operations': top_operations,
            'status': self._get_status(percentage_used)
        }

    def _get_status(self, percentage: float) -> str:
        """Определение статуса квоты"""
        if percentage >= 90:
            return 'critical'
        elif percentage >= 70:
            return 'warning'
        else:
            return 'ok'

    def check_quota_available(self, required: int) -> bool:
        """
        Проверка доступности требуемой квоты

        Args:
            required: Требуемое количество единиц

        Returns:
            bool: Достаточно ли квоты
        """
        remaining = self.get_remaining()
        return remaining >= required

    def get_recommendations(self) -> list:
        """Рекомендации по экономии квоты"""
        stats = self.get_usage_stats()
        recommendations = []

        if stats['percentage_used'] >= 80:
            recommendations.append("⚠️ Использовано более 80% квоты! Включите агрессивное кэширование")

        if stats['percentage_used'] >= 90:
            recommendations.append("🚨 КРИТИЧНО! Используйте только кэшированные данные")

        # Анализ операций
        for op in stats['top_operations']:
            if op['operation'] == 'search' and op['total_cost'] > 500:
                recommendations.append(
                    f"💡 Операция '{op['operation']}' использует много квоты ({op['total_cost']} единиц). "
                    "Рассмотрите кэширование результатов поиска"
                )

        if not recommendations:
            recommendations.append("✅ Использование квоты в норме")

        return recommendations
