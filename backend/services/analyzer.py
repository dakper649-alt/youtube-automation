"""
Модуль для анализа YouTube каналов

Функционал:
- Анализ популярных каналов в нише
- Определение трендовых тем и форматов
- Извлечение метаданных видео (просмотры, лайки, комментарии)
- Анализ конкурентов и их стратегий
- Выявление паттернов успешного контента
- Рекомендации по темам для новых видео

API:
- YouTube Data API v3 для получения данных о каналах и видео
- Аналитика engagement метрик
"""

import re
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from collections import Counter
import asyncio
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import isodate


class YouTubeAnalyzerError(Exception):
    """Базовый класс для ошибок анализатора"""
    pass


class InvalidAPIKeyError(YouTubeAnalyzerError):
    """Неверный API ключ"""
    pass


class ChannelNotFoundError(YouTubeAnalyzerError):
    """Канал не найден"""
    pass


class QuotaExceededError(YouTubeAnalyzerError):
    """Превышена квота API"""
    pass


class YouTubeAnalyzer:
    """Класс для анализа YouTube каналов и видео"""

    def __init__(self, api_key: str):
        """
        Инициализация анализатора

        Args:
            api_key: YouTube Data API ключ

        Raises:
            InvalidAPIKeyError: Если API ключ невалиден
        """
        if not api_key or api_key == "your_youtube_api_key_here":
            raise InvalidAPIKeyError("Необходимо предоставить валидный YouTube API ключ")

        self.api_key = api_key
        try:
            self.youtube = build('youtube', 'v3', developerKey=api_key)
        except Exception as e:
            raise InvalidAPIKeyError(f"Ошибка инициализации YouTube API: {str(e)}")

    def _extract_channel_id(self, channel_url: str) -> str:
        """
        Извлечение ID канала из различных форматов URL

        Args:
            channel_url: URL канала или ID

        Returns:
            str: ID канала

        Raises:
            ValueError: Если не удалось извлечь ID
        """
        # Если это уже ID канала
        if channel_url.startswith('UC') and len(channel_url) == 24:
            return channel_url

        # Паттерны для разных форматов URL
        patterns = [
            r'youtube\.com/channel/(UC[\w-]+)',
            r'youtube\.com/c/([\w-]+)',
            r'youtube\.com/@([\w-]+)',
            r'youtube\.com/user/([\w-]+)',
        ]

        for pattern in patterns:
            match = re.search(pattern, channel_url)
            if match:
                identifier = match.group(1)

                # Если это уже ID канала
                if identifier.startswith('UC'):
                    return identifier

                # Иначе нужно получить ID через API
                try:
                    # Поиск канала по custom URL или username
                    request = self.youtube.search().list(
                        part='snippet',
                        q=identifier,
                        type='channel',
                        maxResults=1
                    )
                    response = request.execute()

                    if response['items']:
                        return response['items'][0]['snippet']['channelId']
                except HttpError:
                    pass

        raise ValueError(f"Не удалось извлечь ID канала из URL: {channel_url}")

    def _extract_video_id(self, video_url: str) -> str:
        """
        Извлечение ID видео из URL

        Args:
            video_url: URL видео или ID

        Returns:
            str: ID видео

        Raises:
            ValueError: Если не удалось извлечь ID
        """
        # Если это уже ID видео
        if len(video_url) == 11 and not '/' in video_url:
            return video_url

        # Паттерны для разных форматов URL
        patterns = [
            r'youtube\.com/watch\?v=([\w-]+)',
            r'youtu\.be/([\w-]+)',
            r'youtube\.com/embed/([\w-]+)',
        ]

        for pattern in patterns:
            match = re.search(pattern, video_url)
            if match:
                return match.group(1)

        raise ValueError(f"Не удалось извлечь ID видео из URL: {video_url}")

    @staticmethod
    def _format_number(num: int) -> str:
        """
        Форматирование больших чисел (1.2M вместо 1200000)

        Args:
            num: Число для форматирования

        Returns:
            str: Отформатированное число
        """
        if num >= 1_000_000_000:
            return f"{num / 1_000_000_000:.1f}B"
        elif num >= 1_000_000:
            return f"{num / 1_000_000:.1f}M"
        elif num >= 1_000:
            return f"{num / 1_000:.1f}K"
        else:
            return str(num)

    @staticmethod
    def _calculate_engagement_rate(views: int, likes: int, comments: int) -> float:
        """
        Расчёт engagement rate

        Args:
            views: Количество просмотров
            likes: Количество лайков
            comments: Количество комментариев

        Returns:
            float: Engagement rate в процентах
        """
        if views == 0:
            return 0.0
        return ((likes + comments) / views) * 100

    def _handle_api_error(self, error: HttpError):
        """
        Обработка ошибок YouTube API

        Args:
            error: Ошибка HTTP

        Raises:
            QuotaExceededError: Если превышена квота
            ChannelNotFoundError: Если канал не найден
            YouTubeAnalyzerError: Другие ошибки
        """
        if error.resp.status == 403:
            if 'quotaExceeded' in str(error):
                raise QuotaExceededError("Превышена квота YouTube API. Попробуйте позже.")
            raise InvalidAPIKeyError("Неверный API ключ или доступ запрещен")
        elif error.resp.status == 404:
            raise ChannelNotFoundError("Канал или видео не найдено")
        else:
            raise YouTubeAnalyzerError(f"Ошибка YouTube API: {str(error)}")

    async def get_channel_info(self, channel_url: str) -> Dict:
        """
        Получить полную информацию о канале

        Args:
            channel_url: URL канала или ID

        Returns:
            dict: Информация о канале

        Raises:
            ChannelNotFoundError: Если канал не найден
            QuotaExceededError: Если превышена квота API
        """
        try:
            channel_id = self._extract_channel_id(channel_url)

            request = self.youtube.channels().list(
                part='snippet,statistics,contentDetails,brandingSettings',
                id=channel_id
            )
            response = request.execute()

            if not response['items']:
                raise ChannelNotFoundError(f"Канал не найден: {channel_url}")

            channel = response['items'][0]
            snippet = channel['snippet']
            statistics = channel['statistics']

            return {
                'id': channel_id,
                'title': snippet['title'],
                'description': snippet.get('description', ''),
                'subscriber_count': int(statistics.get('subscriberCount', 0)),
                'video_count': int(statistics.get('videoCount', 0)),
                'view_count': int(statistics.get('viewCount', 0)),
                'custom_url': snippet.get('customUrl', ''),
                'thumbnail': snippet['thumbnails']['high']['url'],
                'country': snippet.get('country', 'Unknown'),
                'published_at': snippet['publishedAt']
            }

        except HttpError as e:
            self._handle_api_error(e)

    async def get_recent_videos(self, channel_id: str, max_results: int = 10) -> List[Dict]:
        """
        Получить последние видео канала

        Args:
            channel_id: ID канала
            max_results: Максимальное количество видео (по умолчанию 10)

        Returns:
            list: Список словарей с данными о видео

        Raises:
            ChannelNotFoundError: Если канал не найден
        """
        try:
            # Получаем playlist ID для uploads
            channel_request = self.youtube.channels().list(
                part='contentDetails',
                id=channel_id
            )
            channel_response = channel_request.execute()

            if not channel_response['items']:
                raise ChannelNotFoundError(f"Канал не найден: {channel_id}")

            uploads_playlist_id = channel_response['items'][0]['contentDetails']['relatedPlaylists']['uploads']

            # Получаем видео из playlist
            playlist_request = self.youtube.playlistItems().list(
                part='snippet,contentDetails',
                playlistId=uploads_playlist_id,
                maxResults=max_results
            )
            playlist_response = playlist_request.execute()

            videos = []
            video_ids = []

            for item in playlist_response['items']:
                video_id = item['contentDetails']['videoId']
                video_ids.append(video_id)

            # Получаем статистику для всех видео одним запросом
            if video_ids:
                stats_request = self.youtube.videos().list(
                    part='statistics,contentDetails,snippet',
                    id=','.join(video_ids)
                )
                stats_response = stats_request.execute()

                for video in stats_response['items']:
                    stats = video['statistics']
                    snippet = video['snippet']
                    content_details = video['contentDetails']

                    videos.append({
                        'id': video['id'],
                        'title': snippet['title'],
                        'description': snippet.get('description', ''),
                        'published_at': snippet['publishedAt'],
                        'views': int(stats.get('viewCount', 0)),
                        'likes': int(stats.get('likeCount', 0)),
                        'comments': int(stats.get('commentCount', 0)),
                        'duration': content_details['duration'],
                        'tags': snippet.get('tags', [])
                    })

            return videos

        except HttpError as e:
            self._handle_api_error(e)

    async def analyze_video_performance(self, video_id: str) -> Dict:
        """
        Анализ метрик конкретного видео

        Args:
            video_id: ID видео или URL

        Returns:
            dict: Метрики видео

        Raises:
            ChannelNotFoundError: Если видео не найдено
        """
        try:
            video_id = self._extract_video_id(video_id)

            request = self.youtube.videos().list(
                part='statistics,snippet,contentDetails',
                id=video_id
            )
            response = request.execute()

            if not response['items']:
                raise ChannelNotFoundError(f"Видео не найдено: {video_id}")

            video = response['items'][0]
            stats = video['statistics']
            snippet = video['snippet']
            content_details = video['contentDetails']

            views = int(stats.get('viewCount', 0))
            likes = int(stats.get('likeCount', 0))
            comments = int(stats.get('commentCount', 0))

            return {
                'views': views,
                'likes': likes,
                'comments': comments,
                'engagement_rate': self._calculate_engagement_rate(views, likes, comments),
                'title': snippet['title'],
                'description': snippet.get('description', ''),
                'tags': snippet.get('tags', []),
                'duration': content_details['duration'],
                'published_at': snippet['publishedAt']
            }

        except HttpError as e:
            self._handle_api_error(e)

    async def analyze_channel_style(self, channel_id: str) -> Dict:
        """
        Анализ стиля канала на основе последних 20 видео

        Args:
            channel_id: ID канала

        Returns:
            dict: Анализ стиля канала

        Raises:
            ChannelNotFoundError: Если канал не найден
        """
        try:
            videos = await self.get_recent_videos(channel_id, max_results=20)

            if not videos:
                return {
                    'average_views': 0,
                    'average_engagement': 0.0,
                    'posting_frequency': 'unknown',
                    'popular_topics': [],
                    'video_length_avg': 0,
                    'best_performing_titles': [],
                    'common_tags': [],
                    'growth_rate': 0.0
                }

            # Средние просмотры
            total_views = sum(v['views'] for v in videos)
            average_views = total_views // len(videos)

            # Средний engagement
            engagement_rates = [
                self._calculate_engagement_rate(v['views'], v['likes'], v['comments'])
                for v in videos
            ]
            average_engagement = sum(engagement_rates) / len(engagement_rates)

            # Частота публикаций
            if len(videos) >= 2:
                dates = [datetime.fromisoformat(v['published_at'].replace('Z', '+00:00')) for v in videos]
                dates.sort(reverse=True)
                time_diffs = [(dates[i] - dates[i + 1]).days for i in range(len(dates) - 1)]
                avg_days_between = sum(time_diffs) / len(time_diffs) if time_diffs else 0

                if avg_days_between <= 1.5:
                    posting_frequency = "daily"
                elif avg_days_between <= 4:
                    posting_frequency = "2-3 times per week"
                elif avg_days_between <= 8:
                    posting_frequency = "weekly"
                elif avg_days_between <= 15:
                    posting_frequency = "bi-weekly"
                else:
                    posting_frequency = "monthly or less"
            else:
                posting_frequency = "insufficient data"

            # Средняя длина видео
            durations = []
            for v in videos:
                try:
                    duration = isodate.parse_duration(v['duration'])
                    durations.append(int(duration.total_seconds()))
                except:
                    pass
            video_length_avg = sum(durations) // len(durations) if durations else 0

            # Лучшие заголовки (топ-3 по просмотрам)
            sorted_by_views = sorted(videos, key=lambda x: x['views'], reverse=True)
            best_performing_titles = [v['title'] for v in sorted_by_views[:3]]

            # Частые теги
            all_tags = []
            for v in videos:
                all_tags.extend(v['tags'])
            tag_counter = Counter(all_tags)
            common_tags = [tag for tag, count in tag_counter.most_common(10)]

            # Популярные темы (из заголовков)
            title_words = []
            for v in videos:
                words = re.findall(r'\b[A-Za-zА-Яа-я]{4,}\b', v['title'].lower())
                title_words.extend(words)

            # Исключаем стоп-слова
            stop_words = {'this', 'that', 'with', 'from', 'have', 'will', 'your', 'more',
                         'how', 'the', 'and', 'for', 'are', 'but', 'not', 'you', 'all',
                         'это', 'как', 'для', 'что', 'или', 'все', 'это', 'был'}

            filtered_words = [w for w in title_words if w not in stop_words]
            word_counter = Counter(filtered_words)
            popular_topics = [word for word, count in word_counter.most_common(5)]

            return {
                'average_views': average_views,
                'average_engagement': round(average_engagement, 2),
                'posting_frequency': posting_frequency,
                'popular_topics': popular_topics,
                'video_length_avg': video_length_avg,
                'best_performing_titles': best_performing_titles,
                'common_tags': common_tags,
                'growth_rate': 0.0  # Требует исторических данных
            }

        except HttpError as e:
            self._handle_api_error(e)

    async def find_similar_channels(self, channel_id: str, max_results: int = 5) -> List[Dict]:
        """
        Поиск похожих каналов через YouTube Search API

        Args:
            channel_id: ID канала
            max_results: Максимальное количество результатов

        Returns:
            list: Список похожих каналов

        Raises:
            QuotaExceededError: Если превышена квота
        """
        try:
            # Получаем информацию о канале
            channel_info = await self.get_channel_info(channel_id)

            # Извлекаем ключевые слова из описания
            description_words = re.findall(r'\b[A-Za-z]{4,}\b', channel_info['description'])
            search_query = ' '.join(description_words[:5]) if description_words else channel_info['title']

            # Поиск похожих каналов
            request = self.youtube.search().list(
                part='snippet',
                q=search_query,
                type='channel',
                maxResults=max_results + 1,  # +1 потому что может быть сам канал
                order='relevance'
            )
            response = request.execute()

            similar_channels = []
            for item in response['items']:
                found_channel_id = item['snippet']['channelId']

                # Пропускаем сам канал
                if found_channel_id == channel_id:
                    continue

                # Получаем статистику канала
                channel_details = await self.get_channel_info(found_channel_id)
                similar_channels.append(channel_details)

                if len(similar_channels) >= max_results:
                    break

            return similar_channels

        except HttpError as e:
            self._handle_api_error(e)

    async def get_niche_recommendations(self, channel_id: str) -> Dict:
        """
        Рекомендации для создания контента на основе анализа

        Args:
            channel_id: ID канала

        Returns:
            dict: Рекомендации

        Raises:
            ChannelNotFoundError: Если канал не найден
        """
        try:
            style_analysis = await self.analyze_channel_style(channel_id)

            # Рекомендуемая длина видео
            avg_length = style_analysis['video_length_avg']
            if avg_length < 180:
                optimal_length = "Short videos (1-3 minutes) - YouTube Shorts format"
            elif avg_length < 600:
                optimal_length = "Medium videos (5-10 minutes) - good for tutorials"
            elif avg_length < 1200:
                optimal_length = "Long videos (10-20 minutes) - in-depth content"
            else:
                optimal_length = "Extended videos (20+ minutes) - detailed analysis/entertainment"

            # Рекомендуемые темы
            recommended_topics = style_analysis['popular_topics'][:3]
            if not recommended_topics:
                recommended_topics = ["Create content based on trending topics in your niche"]

            # Паттерны заголовков
            title_patterns = []
            for title in style_analysis['best_performing_titles']:
                if '?' in title:
                    title_patterns.append("Questions work well (e.g., 'How to...?', 'Why...?')")
                if any(word in title.lower() for word in ['best', 'top', 'ultimate']):
                    title_patterns.append("Listicles and rankings perform well")
                if len(title) > 60:
                    title_patterns.append("Detailed descriptive titles")

            if not title_patterns:
                title_patterns = ["Use clear, descriptive titles", "Include numbers when possible"]

            # Советы по вовлечению
            engagement_tips = []
            if style_analysis['average_engagement'] < 2:
                engagement_tips.append("Add more call-to-actions in your videos")
                engagement_tips.append("Encourage viewers to comment with questions")
            if style_analysis['average_engagement'] < 5:
                engagement_tips.append("Create polls and community posts")
                engagement_tips.append("Respond to comments to boost engagement")

            engagement_tips.append(f"Your current engagement rate: {style_analysis['average_engagement']:.2f}%")
            engagement_tips.append("Industry average is typically 2-5%")

            return {
                'recommended_topics': recommended_topics,
                'optimal_video_length': optimal_length,
                'posting_schedule': f"Maintain {style_analysis['posting_frequency']} schedule",
                'title_patterns': list(set(title_patterns)),
                'engagement_tips': engagement_tips
            }

        except HttpError as e:
            self._handle_api_error(e)
