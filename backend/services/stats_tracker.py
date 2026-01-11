"""
Stats Tracker - отслеживание статистики генерации видео в SQLite
"""

import sqlite3
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any


class StatsTracker:
    """Трекер статистики для YouTube Automation Studio"""

    def __init__(self, db_path: str = None):
        """
        Инициализация трекера статистики

        Args:
            db_path: Путь к SQLite базе данных (опционально)
        """
        if db_path is None:
            # По умолчанию сохраняем в корень проекта
            db_path = str(Path(__file__).parent.parent.parent / 'stats.db')

        self.db_path = db_path
        self._init_database()

    def _init_database(self):
        """Инициализация базы данных SQLite"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Таблица видео
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS videos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                topic TEXT NOT NULL,
                style TEXT,
                voice TEXT,
                music TEXT,
                duration_seconds INTEGER,
                generation_time_minutes INTEGER,
                success BOOLEAN,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                video_path TEXT
            )
        ''')

        # Таблица использования API
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS api_usage (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                service TEXT NOT NULL,
                requests_count INTEGER DEFAULT 0,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Таблица целей
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS goals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                type TEXT NOT NULL UNIQUE,
                target INTEGER DEFAULT 0,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Инициализация целей по умолчанию
        cursor.execute('''
            INSERT OR IGNORE INTO goals (type, target) VALUES
            ('weekly', 10),
            ('monthly', 40)
        ''')

        conn.commit()
        conn.close()

        print(f"✅ Stats database initialized at {self.db_path}")

    def log_video(self, topic: str, style: str = None, voice: str = None,
                  music: str = None, duration_seconds: int = 0,
                  generation_time_minutes: int = 0, success: bool = True,
                  video_path: str = None):
        """
        Логирование созданного видео

        Args:
            topic: Тема видео
            style: Стиль изображений
            voice: Голос озвучки
            music: Фоновая музыка
            duration_seconds: Длительность видео в секундах
            generation_time_minutes: Время генерации в минутах
            success: Успешность генерации
            video_path: Путь к видео файлу
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO videos (topic, style, voice, music, duration_seconds,
                              generation_time_minutes, success, video_path)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (topic, style, voice, music, duration_seconds,
              generation_time_minutes, success, video_path))

        conn.commit()
        conn.close()

        print(f"📊 Video logged: {topic} ({style}, {voice})")

    def log_api_usage(self, service: str, count: int = 1):
        """
        Логирование использования API

        Args:
            service: Название сервиса (huggingface, elevenlabs, youtube, groq)
            count: Количество запросов
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Проверяем, есть ли запись для сервиса
        cursor.execute('SELECT requests_count FROM api_usage WHERE service = ?', (service,))
        result = cursor.fetchone()

        if result:
            # Обновляем существующую запись
            new_count = result[0] + count
            cursor.execute('''
                UPDATE api_usage
                SET requests_count = ?, last_updated = CURRENT_TIMESTAMP
                WHERE service = ?
            ''', (new_count, service))
        else:
            # Создаём новую запись
            cursor.execute('''
                INSERT INTO api_usage (service, requests_count)
                VALUES (?, ?)
            ''', (service, count))

        conn.commit()
        conn.close()

    def get_stats(self) -> Dict[str, Any]:
        """
        Получить полную статистику

        Returns:
            Словарь со статистикой для dashboard
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Общая статистика
        cursor.execute('''
            SELECT
                COUNT(*) as total_videos,
                SUM(generation_time_minutes) as total_time,
                AVG(CASE WHEN success = 1 THEN 1.0 ELSE 0.0 END) * 100 as success_rate,
                AVG(duration_seconds) as avg_duration
            FROM videos
        ''')
        overview = cursor.fetchone()

        # Видео по дням (последние 7 дней)
        cursor.execute('''
            SELECT
                DATE(created_at) as date,
                COUNT(*) as count
            FROM videos
            WHERE created_at >= datetime('now', '-7 days')
            GROUP BY DATE(created_at)
            ORDER BY date ASC
        ''')
        videos_by_day = [{'date': row[0], 'count': row[1]} for row in cursor.fetchall()]

        # Использование стилей
        cursor.execute('''
            SELECT style, COUNT(*) as count
            FROM videos
            WHERE style IS NOT NULL
            GROUP BY style
            ORDER BY count DESC
            LIMIT 10
        ''')
        style_usage = {row[0]: row[1] for row in cursor.fetchall()}

        # Использование голосов
        cursor.execute('''
            SELECT voice, COUNT(*) as count
            FROM videos
            WHERE voice IS NOT NULL
            GROUP BY voice
            ORDER BY count DESC
            LIMIT 10
        ''')
        voice_usage = {row[0]: row[1] for row in cursor.fetchall()}

        # Время суток
        cursor.execute('''
            SELECT
                CASE
                    WHEN CAST(strftime('%H', created_at) AS INTEGER) BETWEEN 6 AND 11 THEN 'morning'
                    WHEN CAST(strftime('%H', created_at) AS INTEGER) BETWEEN 12 AND 17 THEN 'afternoon'
                    WHEN CAST(strftime('%H', created_at) AS INTEGER) BETWEEN 18 AND 22 THEN 'evening'
                    ELSE 'night'
                END as time_period,
                COUNT(*) as count
            FROM videos
            GROUP BY time_period
        ''')
        time_of_day = {row[0]: row[1] for row in cursor.fetchall()}

        # Заполняем отсутствующие периоды
        for period in ['morning', 'afternoon', 'evening', 'night']:
            if period not in time_of_day:
                time_of_day[period] = 0

        # API Usage
        cursor.execute('SELECT service, requests_count FROM api_usage')
        api_usage_data = {}
        for row in cursor.fetchall():
            service = row[0]
            count = row[1]
            limits = {
                'huggingface': None,
                'elevenlabs': 10000,
                'youtube': 10000,
                'groq': 14400
            }
            api_usage_data[service] = {
                'used': count,
                'limit': limits.get(service, 0)
            }

        # Заполняем отсутствующие сервисы
        for service in ['huggingface', 'elevenlabs', 'youtube', 'groq']:
            if service not in api_usage_data:
                api_usage_data[service] = {
                    'used': 0,
                    'limit': {'huggingface': None, 'elevenlabs': 10000, 'youtube': 10000, 'groq': 14400}[service]
                }

        # Достижения
        total_videos = overview[0] or 0
        cursor.execute('''
            SELECT DATE(created_at) as date, COUNT(*) as count
            FROM videos
            GROUP BY DATE(created_at)
            ORDER BY count DESC
            LIMIT 1
        ''')
        max_per_day = cursor.fetchone()
        max_per_day_count = max_per_day[1] if max_per_day else 0

        cursor.execute('''
            SELECT COUNT(*) as count
            FROM videos
            WHERE created_at >= datetime('now', '-7 days')
        ''')
        weekly_count = cursor.fetchone()[0]

        # Проверка 30-дневной серии
        cursor.execute('''
            SELECT DISTINCT DATE(created_at) as date
            FROM videos
            WHERE created_at >= datetime('now', '-30 days')
            ORDER BY date DESC
        ''')
        dates = [row[0] for row in cursor.fetchall()]
        has_30_day_streak = len(dates) >= 30

        achievements = {
            'first_video': total_videos >= 1,
            'ten_videos': total_videos >= 10,
            'hundred_videos': total_videos >= 100,
            'three_per_day': max_per_day_count >= 3,
            'ten_per_week': weekly_count >= 10,
            'thirty_day_streak': has_30_day_streak
        }

        # Цели
        cursor.execute('SELECT type, target FROM goals')
        goals_data = {}
        for row in cursor.fetchall():
            goal_type = row[0]
            target = row[1]

            # Подсчитываем текущий прогресс
            if goal_type == 'weekly':
                cursor.execute('''
                    SELECT COUNT(*) FROM videos
                    WHERE created_at >= datetime('now', '-7 days')
                ''')
                current = cursor.fetchone()[0]
            elif goal_type == 'monthly':
                cursor.execute('''
                    SELECT COUNT(*) FROM videos
                    WHERE created_at >= datetime('now', '-30 days')
                ''')
                current = cursor.fetchone()[0]
            else:
                current = 0

            goals_data[goal_type] = {
                'current': current,
                'target': target
            }

        conn.close()

        # Формируем результат
        stats = {
            'overview': {
                'totalVideos': overview[0] or 0,
                'totalTimeMinutes': overview[1] or 0,
                'successRate': round(overview[2] or 0, 1),
                'avgDurationSeconds': int(overview[3] or 0)
            },
            'videosByDay': videos_by_day,
            'styleUsage': style_usage,
            'voiceUsage': voice_usage,
            'timeOfDay': time_of_day,
            'apiUsage': api_usage_data,
            'achievements': achievements,
            'goals': goals_data
        }

        return stats

    def update_goal(self, goal_type: str, target: int):
        """
        Обновить цель

        Args:
            goal_type: Тип цели (weekly, monthly)
            target: Новое значение цели
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            UPDATE goals
            SET target = ?, last_updated = CURRENT_TIMESTAMP
            WHERE type = ?
        ''', (target, goal_type))

        conn.commit()
        conn.close()

        print(f"✅ Goal updated: {goal_type} = {target}")

    def reset_stats(self):
        """Сброс всей статистики (для тестирования)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('DELETE FROM videos')
        cursor.execute('DELETE FROM api_usage')

        conn.commit()
        conn.close()

        print("✅ Stats reset")


# Тестирование
if __name__ == '__main__':
    print("\n" + "=" * 80)
    print("📊 STATS TRACKER TEST")
    print("=" * 80)

    tracker = StatsTracker()

    # Добавляем тестовые данные
    tracker.log_video(
        topic="Test Video 1",
        style="minimalist_stick_figure",
        voice="rachel",
        music="calm_piano",
        duration_seconds=185,
        generation_time_minutes=5,
        success=True
    )

    tracker.log_api_usage('huggingface', 10)
    tracker.log_api_usage('elevenlabs', 1)

    # Получаем статистику
    stats = tracker.get_stats()

    print("\n📊 Stats:")
    print(json.dumps(stats, indent=2, ensure_ascii=False))

    print("\n" + "=" * 80)
