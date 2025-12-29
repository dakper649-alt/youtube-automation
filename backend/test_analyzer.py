#!/usr/bin/env python3
"""
Тестовый скрипт для анализатора YouTube каналов

Использование:
    python test_analyzer.py <CHANNEL_URL>

Примеры:
    python test_analyzer.py https://www.youtube.com/@mkbhd
    python test_analyzer.py UCBJycsmduvYEL83R_U4JriQ
"""

import asyncio
import sys
import os
from dotenv import load_dotenv

# Добавляем путь к модулям
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from services.analyzer import (
    YouTubeAnalyzer,
    InvalidAPIKeyError,
    ChannelNotFoundError,
    QuotaExceededError,
    YouTubeAnalyzerError
)


def print_section(title: str):
    """Печать разделителя секции"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)


def print_channel_info(info: dict):
    """Красивый вывод информации о канале"""
    print_section("ИНФОРМАЦИЯ О КАНАЛЕ")
    print(f"📺 Название:       {info['title']}")
    print(f"🆔 ID:            {info['id']}")
    print(f"🔗 Custom URL:    {info['custom_url']}")
    print(f"👥 Подписчики:    {YouTubeAnalyzer._format_number(info['subscriber_count'])}")
    print(f"🎬 Видео:         {info['video_count']}")
    print(f"👁  Просмотры:     {YouTubeAnalyzer._format_number(info['view_count'])}")
    print(f"🌍 Страна:        {info['country']}")
    print(f"📅 Создан:        {info['published_at'][:10]}")

    if info['description']:
        description = info['description'][:200] + "..." if len(info['description']) > 200 else info['description']
        print(f"\n📝 Описание:\n{description}")


def print_recent_videos(videos: list):
    """Красивый вывод последних видео"""
    print_section("ПОСЛЕДНИЕ 5 ВИДЕО")

    for i, video in enumerate(videos[:5], 1):
        engagement = YouTubeAnalyzer._calculate_engagement_rate(
            video['views'], video['likes'], video['comments']
        )

        print(f"\n{i}. {video['title']}")
        print(f"   👁  Просмотры:     {YouTubeAnalyzer._format_number(video['views'])}")
        print(f"   👍 Лайки:         {YouTubeAnalyzer._format_number(video['likes'])}")
        print(f"   💬 Комментарии:   {YouTubeAnalyzer._format_number(video['comments'])}")
        print(f"   📊 Engagement:    {engagement:.2f}%")
        print(f"   📅 Опубликовано:  {video['published_at'][:10]}")


def print_channel_style(style: dict):
    """Красивый вывод анализа стиля канала"""
    print_section("АНАЛИЗ СТИЛЯ КАНАЛА")

    print(f"📊 Средние просмотры:          {YouTubeAnalyzer._format_number(style['average_views'])}")
    print(f"📈 Средний engagement:         {style['average_engagement']:.2f}%")
    print(f"📅 Частота публикаций:         {style['posting_frequency']}")
    print(f"⏱  Средняя длина видео:        {style['video_length_avg'] // 60} мин {style['video_length_avg'] % 60} сек")

    if style['popular_topics']:
        print(f"\n🔥 Популярные темы:")
        for i, topic in enumerate(style['popular_topics'], 1):
            print(f"   {i}. {topic}")

    if style['best_performing_titles']:
        print(f"\n🏆 Лучшие заголовки:")
        for i, title in enumerate(style['best_performing_titles'], 1):
            print(f"   {i}. {title}")

    if style['common_tags']:
        print(f"\n🏷  Частые теги:")
        tags_str = ", ".join(style['common_tags'][:10])
        print(f"   {tags_str}")


def print_recommendations(recommendations: dict):
    """Красивый вывод рекомендаций"""
    print_section("РЕКОМЕНДАЦИИ ДЛЯ СОЗДАНИЯ КОНТЕНТА")

    print(f"\n⏱  Оптимальная длина видео:")
    print(f"   {recommendations['optimal_video_length']}")

    print(f"\n📅 График публикаций:")
    print(f"   {recommendations['posting_schedule']}")

    if recommendations['recommended_topics']:
        print(f"\n🎯 Рекомендуемые темы:")
        for i, topic in enumerate(recommendations['recommended_topics'], 1):
            print(f"   {i}. {topic}")

    if recommendations['title_patterns']:
        print(f"\n📝 Паттерны заголовков:")
        for i, pattern in enumerate(recommendations['title_patterns'], 1):
            print(f"   {i}. {pattern}")

    if recommendations['engagement_tips']:
        print(f"\n💡 Советы по вовлечению:")
        for i, tip in enumerate(recommendations['engagement_tips'], 1):
            print(f"   {i}. {tip}")


def print_similar_channels(channels: list):
    """Красивый вывод похожих каналов"""
    print_section("ПОХОЖИЕ КАНАЛЫ")

    for i, channel in enumerate(channels, 1):
        print(f"\n{i}. {channel['title']}")
        print(f"   👥 Подписчики:  {YouTubeAnalyzer._format_number(channel['subscriber_count'])}")
        print(f"   🎬 Видео:       {channel['video_count']}")
        print(f"   👁  Просмотры:   {YouTubeAnalyzer._format_number(channel['view_count'])}")
        if channel['custom_url']:
            print(f"   🔗 URL:         youtube.com/{channel['custom_url']}")


async def analyze_channel(api_key: str, channel_url: str):
    """
    Полный анализ канала

    Args:
        api_key: YouTube API ключ
        channel_url: URL канала или ID
    """
    try:
        # Инициализация анализатора
        print("🚀 Инициализация YouTube Analyzer...")
        analyzer = YouTubeAnalyzer(api_key)

        # Получение информации о канале
        print("📡 Получение информации о канале...")
        channel_info = await analyzer.get_channel_info(channel_url)
        print_channel_info(channel_info)

        channel_id = channel_info['id']

        # Получение последних видео
        print("\n📡 Получение последних видео...")
        recent_videos = await analyzer.get_recent_videos(channel_id, max_results=10)
        print_recent_videos(recent_videos)

        # Анализ стиля канала
        print("\n📡 Анализ стиля канала...")
        channel_style = await analyzer.analyze_channel_style(channel_id)
        print_channel_style(channel_style)

        # Получение рекомендаций
        print("\n📡 Генерация рекомендаций...")
        recommendations = await analyzer.get_niche_recommendations(channel_id)
        print_recommendations(recommendations)

        # Поиск похожих каналов
        print("\n📡 Поиск похожих каналов...")
        similar_channels = await analyzer.find_similar_channels(channel_id, max_results=3)
        print_similar_channels(similar_channels)

        print_section("АНАЛИЗ ЗАВЕРШЕН")
        print("✅ Все данные успешно получены!")

    except InvalidAPIKeyError as e:
        print(f"\n❌ ОШИБКА: Неверный API ключ")
        print(f"   {str(e)}")
        print("\n💡 Как получить API ключ:")
        print("   1. Перейдите на https://console.cloud.google.com/")
        print("   2. Создайте новый проект")
        print("   3. Включите YouTube Data API v3")
        print("   4. Создайте API ключ в разделе 'Credentials'")
        print("   5. Добавьте ключ в .env файл: YOUTUBE_API_KEY=your_key")
        sys.exit(1)

    except ChannelNotFoundError as e:
        print(f"\n❌ ОШИБКА: Канал не найден")
        print(f"   {str(e)}")
        print("\n💡 Убедитесь что URL канала корректен:")
        print("   - https://www.youtube.com/@channelname")
        print("   - https://www.youtube.com/channel/UC...")
        print("   - или просто ID канала (UC...)")
        sys.exit(1)

    except QuotaExceededError as e:
        print(f"\n❌ ОШИБКА: Превышена квота API")
        print(f"   {str(e)}")
        print("\n💡 Квота YouTube API:")
        print("   - Бесплатный лимит: 10,000 единиц в день")
        print("   - Попробуйте позже или используйте другой API ключ")
        sys.exit(1)

    except YouTubeAnalyzerError as e:
        print(f"\n❌ ОШИБКА: {str(e)}")
        sys.exit(1)

    except Exception as e:
        print(f"\n❌ НЕОЖИДАННАЯ ОШИБКА: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


def main():
    """Главная функция"""
    # Загрузка переменных окружения
    load_dotenv()

    # Проверка аргументов
    if len(sys.argv) < 2:
        print("❌ ОШИБКА: Не указан URL канала")
        print("\nИспользование:")
        print("    python test_analyzer.py <CHANNEL_URL>")
        print("\nПримеры:")
        print("    python test_analyzer.py https://www.youtube.com/@mkbhd")
        print("    python test_analyzer.py UCBJycsmduvYEL83R_U4JriQ")
        print("    python test_analyzer.py https://www.youtube.com/channel/UCBJycsmduvYEL83R_U4JriQ")
        sys.exit(1)

    channel_url = sys.argv[1]

    # Получение API ключа
    api_key = os.getenv('YOUTUBE_API_KEY')

    if not api_key or api_key == 'your_youtube_api_key_here':
        print("❌ ОШИБКА: YouTube API ключ не найден")
        print("\n💡 Создайте файл .env и добавьте:")
        print("   YOUTUBE_API_KEY=your_actual_api_key_here")
        print("\n💡 Или экспортируйте переменную окружения:")
        print("   export YOUTUBE_API_KEY=your_actual_api_key_here")
        sys.exit(1)

    # Запуск анализа
    print("=" * 80)
    print("  🎬 YouTube Channel Analyzer")
    print("=" * 80)
    print(f"\n📍 Канал: {channel_url}")

    asyncio.run(analyze_channel(api_key, channel_url))


if __name__ == "__main__":
    main()
