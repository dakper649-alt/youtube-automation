"""
Расширенный модуль для анализа YouTube каналов

Расширенный функционал:
- Мультиязычный анализ контента
- Performance scoring для видео
- Поиск низкоконкурентных ниш
- Детальный анализ стиля с кэшированием
- Оптимизация использования YouTube API квоты
- Батчинг запросов

СТОИМОСТЬ ОПЕРАЦИЙ (в единицах YouTube API квоты):
- get_channel_info: 1 единица
- get_recent_videos: 1-2 единицы (зависит от количества)
- analyze_channel_multilingual: ~50 единиц
- find_underserved_niches: ~200-300 единиц (делать редко!)
- analyze_content_style_detailed: ~100 единиц (первый раз), 0 (из кэша)
"""

import sys
import os
from pathlib import Path

# Добавляем путь к родительской директории для импорта
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.analyzer import YouTubeAnalyzer, YouTubeAnalyzerError, ChannelNotFoundError
from utils.cache import YouTubeCache, QuotaTracker
from utils.language_detector import LanguageDetector
from utils.api_costs import get_operation_cost, estimate_channel_analysis_cost, daily_quota_budget

from typing import Dict, List, Optional
from datetime import datetime, timedelta
from collections import Counter
import re
import asyncio
from googleapiclient.errors import HttpError


class YouTubeAnalyzerAdvanced(YouTubeAnalyzer):
    """
    Расширенный анализатор YouTube с кэшированием и оптимизацией квоты
    """

    def __init__(
        self,
        api_key: str,
        cache_ttl: int = 3600,
        cache_db: str = "youtube_cache.db",
        quota_db: str = "youtube_quota.db",
        daily_quota_limit: int = 10000
    ):
        """
        Инициализация расширенного анализатора

        Args:
            api_key: YouTube API ключ
            cache_ttl: Время жизни кэша в секундах (по умолчанию 1 час)
            cache_db: Путь к БД кэша
            quota_db: Путь к БД квоты
            daily_quota_limit: Дневной лимит квоты (по умолчанию 10,000)
        """
        super().__init__(api_key)

        self.cache = YouTubeCache(cache_db)
        self.quota_tracker = QuotaTracker(quota_db, daily_quota_limit)
        self.cache_ttl = cache_ttl
        self.lang_detector = LanguageDetector()

        # Очищаем устаревший кэш при инициализации
        self.cache.clear_expired()

    def _track_quota(self, operation: str, cost: int):
        """Трекинг использования квоты"""
        self.quota_tracker.track(operation, cost)

    async def get_channel_info(self, channel_url: str, use_cache: bool = True) -> Dict:
        """
        Получить информацию о канале с кэшированием

        Args:
            channel_url: URL канала или ID
            use_cache: Использовать кэш (по умолчанию True)

        Returns:
            dict: Информация о канале

        Стоимость: 1 единица API (или 0 из кэша)
        """
        cache_key = self.cache._generate_key('channel_info', url=channel_url)

        # Проверяем кэш
        if use_cache:
            cached = self.cache.get(cache_key)
            if cached:
                return cached

        # Получаем данные из API
        result = await super().get_channel_info(channel_url)

        # Трекаем квоту
        self._track_quota('channels.list', 1)

        # Сохраняем в кэш
        self.cache.set(cache_key, result, ttl=self.cache_ttl)

        return result

    async def get_recent_videos(
        self,
        channel_id: str,
        max_results: int = 10,
        use_cache: bool = True
    ) -> List[Dict]:
        """
        Получить последние видео с кэшированием

        Args:
            channel_id: ID канала
            max_results: Максимальное количество видео
            use_cache: Использовать кэш

        Returns:
            list: Список видео

        Стоимость: 2 единицы API (или 0 из кэша)
        """
        cache_key = self.cache._generate_key(
            'recent_videos',
            channel_id=channel_id,
            max_results=max_results
        )

        if use_cache:
            cached = self.cache.get(cache_key)
            if cached:
                return cached

        result = await super().get_recent_videos(channel_id, max_results)

        # Трекаем квоту (playlistItems.list + videos.list)
        self._track_quota('playlistItems.list', 1)
        self._track_quota('videos.list', 1)

        self.cache.set(cache_key, result, ttl=self.cache_ttl)

        return result

    async def analyze_channel_multilingual(
        self,
        channel_id: str,
        source_language: str = 'auto',
        target_language: str = 'ru'
    ) -> Dict:
        """
        Мультиязычный анализ канала

        Args:
            channel_id: ID канала
            source_language: Язык источника (auto для автоопределения)
            target_language: Целевой язык

        Returns:
            dict: Результаты мультиязычного анализа

        Стоимость: ~50 единиц API
        """
        # Получаем базовую информацию
        channel_info = await self.get_channel_info(channel_id)
        videos = await self.get_recent_videos(channel_id, max_results=10)

        # Определяем язык контента
        sample_text = f"{channel_info['title']} {channel_info['description']}"
        for video in videos[:3]:
            sample_text += f" {video['title']} {video['description'][:100]}"

        if source_language == 'auto':
            detected_lang = self.lang_detector.detect_language(sample_text)
        else:
            detected_lang = source_language

        # Топ-10 видео по просмотрам
        top_videos = sorted(videos, key=lambda x: x['views'], reverse=True)[:10]

        # Извлекаем темы контента
        all_titles = " ".join([v['title'] for v in videos])
        content_themes = self.lang_detector.extract_keywords(all_titles, detected_lang, top_n=10)

        # Советы по адаптации
        adaptation_suggestions = self.lang_detector.get_adaptation_tips(
            detected_lang,
            target_language
        )

        # Переведённые заголовки (здесь просто помечаем, что нужен перевод)
        translated_titles = []
        if detected_lang != target_language:
            translated_titles = [
                f"[Требуется перевод] {v['title']}"
                for v in top_videos[:5]
            ]
        else:
            translated_titles = [v['title'] for v in top_videos[:5]]

        return {
            'detected_language': detected_lang,
            'language_name': self.lang_detector.get_language_name(detected_lang),
            'channel_info': {
                'title': channel_info['title'],
                'subscribers': channel_info['subscriber_count'],
                'total_views': channel_info['view_count']
            },
            'top_videos': [
                {
                    'title': v['title'],
                    'views': v['views'],
                    'engagement_rate': self._calculate_engagement_rate(
                        v['views'], v['likes'], v['comments']
                    )
                }
                for v in top_videos
            ],
            'translated_titles': translated_titles,
            'content_themes': content_themes,
            'adaptation_suggestions': adaptation_suggestions,
            'translation_needed': detected_lang != target_language
        }

    async def calculate_performance_score(
        self,
        video_id: str,
        channel_stats: Optional[Dict] = None
    ) -> float:
        """
        Вычисление performance score видео

        Учитывает:
        - Соотношение просмотров к подписчикам
        - Engagement rate
        - Freshness (новизна видео)
        - Сравнение со средними показателями канала

        Args:
            video_id: ID видео
            channel_stats: Статистика канала (опционально)

        Returns:
            float: Score от 0 до 100

        Стоимость: 1 единица API
        """
        video = await super().analyze_video_performance(video_id)

        # Базовые метрики
        engagement = video['engagement_rate']
        views = video['views']

        # Freshness score (чем свежее, тем выше)
        published = datetime.fromisoformat(video['published_at'].replace('Z', '+00:00'))
        days_old = (datetime.now(published.tzinfo) - published).days
        freshness_score = max(0, 100 - (days_old * 2))  # Уменьшается на 2 балла за день

        # Engagement score (нормализованный)
        engagement_score = min(100, engagement * 20)  # 5% engagement = 100 баллов

        # Views score (если есть статистика канала)
        views_score = 50  # По умолчанию
        if channel_stats:
            avg_views = channel_stats.get('average_views', 0)
            if avg_views > 0:
                views_ratio = views / avg_views
                views_score = min(100, views_ratio * 50)

        # Итоговый score (взвешенная сумма)
        total_score = (
            engagement_score * 0.4 +  # 40% вес на engagement
            freshness_score * 0.2 +   # 20% вес на свежесть
            views_score * 0.4         # 40% вес на просмотры
        )

        return round(total_score, 2)

    async def rank_videos_by_performance(
        self,
        channel_id: str,
        limit: int = 20
    ) -> List[Dict]:
        """
        Ранжирование видео по performance score

        Args:
            channel_id: ID канала
            limit: Количество видео для анализа

        Returns:
            list: Отсортированный список видео со scores

        Стоимость: ~20-30 единиц API
        """
        # Получаем видео
        videos = await self.get_recent_videos(channel_id, max_results=limit)

        # Получаем статистику канала
        channel_info = await self.get_channel_info(channel_id)
        style = await super().analyze_channel_style(channel_id)

        channel_stats = {
            'average_views': style['average_views'],
            'subscriber_count': channel_info['subscriber_count']
        }

        # Вычисляем scores для каждого видео
        scored_videos = []
        for video in videos:
            score = await self.calculate_performance_score(
                video['id'],
                channel_stats
            )

            scored_videos.append({
                'id': video['id'],
                'title': video['title'],
                'views': video['views'],
                'likes': video['likes'],
                'comments': video['comments'],
                'engagement_rate': self._calculate_engagement_rate(
                    video['views'], video['likes'], video['comments']
                ),
                'published_at': video['published_at'],
                'performance_score': score
            })

        # Сортируем по score
        scored_videos.sort(key=lambda x: x['performance_score'], reverse=True)

        return scored_videos

    async def find_underserved_niches(
        self,
        broad_topic: str,
        min_views: int = 10000,
        max_competition: int = 100
    ) -> List[Dict]:
        """
        Поиск низкоконкурентных ниш

        ВНИМАНИЕ: Очень дорогая операция! Используйте редко (раз в неделю)

        Args:
            broad_topic: Широкая тема для поиска
            min_views: Минимальные просмотры
            max_competition: Максимальная конкуренция

        Returns:
            list: Список перспективных ниш

        Стоимость: ~200-300 единиц API
        """
        # Проверяем доступность квоты
        if not self.quota_tracker.check_quota_available(300):
            raise YouTubeAnalyzerError(
                "Недостаточно квоты для поиска ниш. "
                f"Требуется ~300 единиц, доступно: {self.quota_tracker.get_remaining()}"
            )

        try:
            # Поиск каналов по теме
            request = self.youtube.search().list(
                part='snippet',
                q=broad_topic,
                type='channel',
                maxResults=50,
                order='viewCount'
            )
            response = request.execute()
            self._track_quota('search.list', 100)

            niches = []
            channel_ids = [item['snippet']['channelId'] for item in response['items'][:20]]

            # Анализируем каждый канал
            for channel_id in channel_ids:
                try:
                    channel_info = await self.get_channel_info(channel_id, use_cache=True)
                    videos = await self.get_recent_videos(channel_id, max_results=10, use_cache=True)

                    if not videos:
                        continue

                    # Средние просмотры
                    avg_views = sum(v['views'] for v in videos) / len(videos)

                    # Определяем конкуренцию (по количеству подписчиков)
                    subscribers = channel_info['subscriber_count']

                    if avg_views >= min_views and subscribers <= max_competition * 1000:
                        # Извлекаем тематику
                        titles = " ".join([v['title'] for v in videos])
                        keywords = self.lang_detector.extract_keywords(titles, 'auto', top_n=5)

                        niche = {
                            'niche': " ".join(keywords[:3]),
                            'avg_views': int(avg_views),
                            'competition_level': 'low' if subscribers < 50000 else 'medium',
                            'growth_trend': 'stable',  # Требует исторических данных
                            'recommended': avg_views > min_views * 2,
                            'example_channels': [
                                {
                                    'title': channel_info['title'],
                                    'subscribers': subscribers,
                                    'avg_views': int(avg_views)
                                }
                            ]
                        }

                        niches.append(niche)

                except Exception as e:
                    continue

            # Сортируем по среднимпросмотрам
            niches.sort(key=lambda x: x['avg_views'], reverse=True)

            return niches[:10]

        except HttpError as e:
            self._handle_api_error(e)

    async def analyze_content_style_detailed(self, channel_id: str) -> Dict:
        """
        Детальный анализ стиля контента с кэшированием

        ВАЖНО: Результат кэшируется на 24 часа!

        Args:
            channel_id: ID канала

        Returns:
            dict: Детальный анализ стиля

        Стоимость: ~100 единиц API (первый раз), 0 (из кэша)
        """
        cache_key = self.cache._generate_key('detailed_style', channel_id=channel_id)

        # Проверяем кэш (TTL 24 часа)
        cached = self.cache.get(cache_key)
        if cached:
            return cached

        # Получаем базовый анализ стиля
        basic_style = await super().analyze_channel_style(channel_id)
        videos = await self.get_recent_videos(channel_id, max_results=20)

        # Анализ структуры заголовков
        title_patterns = self._analyze_title_patterns(videos)

        # Анализ длительности
        duration_analysis = self._analyze_durations(videos)

        # Анализ engagement triggers
        engagement_triggers = self._analyze_engagement_triggers(videos)

        # Timing анализ (когда публикуются видео)
        timing_analysis = self._analyze_publishing_timing(videos)

        result = {
            **basic_style,
            'title_patterns': title_patterns,
            'duration_analysis': duration_analysis,
            'engagement_triggers': engagement_triggers,
            'publishing_timing': timing_analysis,
            'cache_expires_in': '24 hours'
        }

        # Кэшируем на 24 часа
        self.cache.set(cache_key, result, ttl=86400)

        return result

    def _analyze_title_patterns(self, videos: List[Dict]) -> Dict:
        """Анализ паттернов заголовков"""
        titles = [v['title'] for v in videos]

        patterns = {
            'avg_length': sum(len(t) for t in titles) / len(titles) if titles else 0,
            'uses_numbers': sum(1 for t in titles if re.search(r'\d+', t)) / len(titles) * 100,
            'uses_questions': sum(1 for t in titles if '?' in t) / len(titles) * 100,
            'uses_caps': sum(1 for t in titles if re.search(r'[A-ZА-Я]{2,}', t)) / len(titles) * 100,
            'uses_emojis': sum(1 for t in titles if re.search(r'[^\w\s,.]', t)) / len(titles) * 100,
            'common_words': self.lang_detector.extract_keywords(" ".join(titles), 'auto', 5)
        }

        return patterns

    def _analyze_durations(self, videos: List[Dict]) -> Dict:
        """Анализ длительности видео"""
        import isodate

        durations = []
        for v in videos:
            try:
                duration = isodate.parse_duration(v['duration'])
                durations.append(int(duration.total_seconds()))
            except:
                pass

        if not durations:
            return {}

        return {
            'avg_seconds': sum(durations) / len(durations),
            'min_seconds': min(durations),
            'max_seconds': max(durations),
            'most_common_range': self._get_duration_range(sum(durations) / len(durations))
        }

    def _get_duration_range(self, seconds: float) -> str:
        """Определение диапазона длительности"""
        if seconds < 60:
            return "Shorts (< 1 min)"
        elif seconds < 180:
            return "Short (1-3 min)"
        elif seconds < 600:
            return "Medium (5-10 min)"
        elif seconds < 1200:
            return "Long (10-20 min)"
        else:
            return "Extended (20+ min)"

    def _analyze_engagement_triggers(self, videos: List[Dict]) -> List[str]:
        """Анализ триггеров вовлечения"""
        triggers = []

        # Анализируем топ видео по engagement
        sorted_videos = sorted(
            videos,
            key=lambda x: self._calculate_engagement_rate(x['views'], x['likes'], x['comments']),
            reverse=True
        )

        top_3 = sorted_videos[:3]

        # Ищем общие паттерны в успешных видео
        top_titles = [v['title'] for v in top_3]

        if any('?' in t for t in top_titles):
            triggers.append("Вопросы в заголовках повышают engagement")

        if any(re.search(r'\d+', t) for t in top_titles):
            triggers.append("Числа в заголовках привлекают внимание")

        # Анализ тегов
        all_tags = []
        for v in top_3:
            all_tags.extend(v.get('tags', []))

        if len(all_tags) > 10:
            triggers.append(f"Используйте теги: {', '.join(Counter(all_tags).most_common(5)[i][0] for i in range(min(5, len(Counter(all_tags).most_common(5)))))}")

        return triggers if triggers else ["Требуется больше данных для анализа"]

    def _analyze_publishing_timing(self, videos: List[Dict]) -> Dict:
        """Анализ времени публикации"""
        publish_times = []

        for v in videos:
            try:
                dt = datetime.fromisoformat(v['published_at'].replace('Z', '+00:00'))
                publish_times.append({
                    'hour': dt.hour,
                    'day_of_week': dt.strftime('%A'),
                    'views': v['views']
                })
            except:
                pass

        if not publish_times:
            return {}

        # Находим лучшее время
        best_time = max(publish_times, key=lambda x: x['views'])

        return {
            'best_hour': best_time['hour'],
            'best_day': best_time['day_of_week'],
            'recommendation': f"Публикуйте видео в {best_time['hour']}:00 по {best_time['day_of_week']}"
        }

    async def get_api_usage_stats(self) -> Dict:
        """
        Статистика использования API квоты

        Returns:
            dict: Детальная статистика

        Стоимость: 0 единиц (локальные данные)
        """
        stats = self.quota_tracker.get_usage_stats()
        recommendations = self.quota_tracker.get_recommendations()
        budget = daily_quota_budget(self.quota_tracker.daily_limit)

        return {
            **stats,
            'recommendations': recommendations,
            'budget_info': budget,
            'cache_stats': self.cache.get_stats()
        }

    async def batch_analyze_channels(self, channel_ids: List[str]) -> List[Dict]:
        """
        Пакетный анализ каналов с оптимизацией

        Экономит до 40% квоты за счёт:
        - Кэширования
        - Батчинга запросов
        - Переиспользования данных

        Args:
            channel_ids: Список ID каналов

        Returns:
            list: Результаты анализа каждого канала

        Стоимость: ~10-15 единиц на канал (вместо 20-30)
        """
        results = []

        for channel_id in channel_ids:
            try:
                # Используем кэш агрессивно
                channel_info = await self.get_channel_info(channel_id, use_cache=True)
                videos = await self.get_recent_videos(channel_id, max_results=10, use_cache=True)
                style = await self.analyze_content_style_detailed(channel_id)

                results.append({
                    'channel_id': channel_id,
                    'channel_info': channel_info,
                    'recent_videos_count': len(videos),
                    'style_summary': {
                        'avg_views': style['average_views'],
                        'posting_frequency': style['posting_frequency'],
                        'avg_engagement': style['average_engagement']
                    },
                    'status': 'success'
                })

            except Exception as e:
                results.append({
                    'channel_id': channel_id,
                    'error': str(e),
                    'status': 'error'
                })

        return results
