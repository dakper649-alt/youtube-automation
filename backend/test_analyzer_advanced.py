#!/usr/bin/env python3
"""
Тестовый скрипт для расширенного анализатора YouTube каналов

Демонстрирует:
- Работу с кэшем
- Трекинг квоты API
- Мультиязычный анализ
- Performance scoring
- Поиск низкоконкурентных ниш
- Детальный анализ стиля

Использование:
    python test_analyzer_advanced.py <CHANNEL_URL> [--mode MODE]

Режимы:
    full        - Полный анализ (по умолчанию)
    multilang   - Мультиязычный анализ
    performance - Анализ производительности видео
    niches      - Поиск ниш (дорого!)
    batch       - Пакетный анализ нескольких каналов
    quota       - Показать статистику квоты

Примеры:
    python test_analyzer_advanced.py https://www.youtube.com/@mkbhd
    python test_analyzer_advanced.py UCBJycsmduvYEL83R_U4JriQ --mode performance
    python test_analyzer_advanced.py --mode quota
"""

import asyncio
import sys
import os
from dotenv import load_dotenv
import argparse

# Добавляем путь к модулям
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from services.analyzer_advanced import YouTubeAnalyzerAdvanced
from services.analyzer import InvalidAPIKeyError, ChannelNotFoundError, QuotaExceededError


def print_section(title: str, emoji: str = ""):
    """Печать красивого разделителя"""
    print("\n" + "=" * 80)
    print(f"  {emoji} {title}")
    print("=" * 80)


def print_quota_stats(stats: dict):
    """Вывод статистики квоты"""
    print_section("СТАТИСТИКА ИСПОЛЬЗОВАНИЯ YOUTUBE API КВОТЫ", "📊")

    print(f"📅 Дата: {stats['date']}")
    print(f"💰 Использовано сегодня: {stats['used_today']:,} / {stats['daily_limit']:,} единиц")
    print(f"⚡ Осталось: {stats['remaining']:,} единиц ({100 - stats['percentage_used']:.1f}%)")

    # Цветной индикатор
    if stats['status'] == 'critical':
        print("🚨 СТАТУС: КРИТИЧЕСКИЙ - Квота почти исчерпана!")
    elif stats['status'] == 'warning':
        print("⚠️  СТАТУС: ПРЕДУПРЕЖДЕНИЕ - Используйте квоту аккуратно")
    else:
        print("✅ СТАТУС: Нормально")

    if stats['top_operations']:
        print(f"\n🔝 Топ операций сегодня:")
        for i, op in enumerate(stats['top_operations'][:5], 1):
            print(f"   {i}. {op['operation']}: {op['total_cost']} единиц ({op['count']} запросов)")

    print(f"\n💡 Рекомендации:")
    for rec in stats['recommendations']:
        print(f"   • {rec}")

    # Бюджет
    budget = stats['budget_info']
    print(f"\n💵 Рекомендованный бюджет на канал:")
    print(f"   • 3 канала: {budget['recommended_per_channel']['3_channels']:,} единиц/канал")
    print(f"   • 5 каналов: {budget['recommended_per_channel']['5_channels']:,} единиц/канал")
    print(f"   • 10 каналов: {budget['recommended_per_channel']['10_channels']:,} единиц/канал")

    # Кэш
    cache = stats['cache_stats']
    print(f"\n💾 Статистика кэша:")
    print(f"   • Всего записей: {cache['total_entries']}")
    print(f"   • Актуальных: {cache['valid_entries']}")
    print(f"   • Размер БД: {cache['db_size_mb']} MB")


async def test_full_analysis(analyzer: YouTubeAnalyzerAdvanced, channel_url: str):
    """Полный анализ канала"""
    print_section("ПОЛНЫЙ АНАЛИЗ КАНАЛА", "🎬")

    # Засекаем квоту до начала
    stats_before = await analyzer.get_api_usage_stats()
    quota_before = stats_before['used_today']

    # Получаем информацию о канале
    print("\n1️⃣ Получение базовой информации...")
    channel_info = await analyzer.get_channel_info(channel_url)

    print(f"   📺 Канал: {channel_info['title']}")
    print(f"   👥 Подписчики: {analyzer._format_number(channel_info['subscriber_count'])}")
    print(f"   🎬 Видео: {channel_info['video_count']}")

    channel_id = channel_info['id']

    # Последние видео
    print("\n2️⃣ Анализ последних 10 видео...")
    videos = await analyzer.get_recent_videos(channel_id, max_results=10)
    print(f"   ✅ Получено {len(videos)} видео")

    # Детальный анализ стиля
    print("\n3️⃣ Детальный анализ стиля (с кэшированием)...")
    style = await analyzer.analyze_content_style_detailed(channel_id)

    print(f"   📊 Средние просмотры: {analyzer._format_number(style['average_views'])}")
    print(f"   📈 Engagement: {style['average_engagement']:.2f}%")
    print(f"   📅 Частота: {style['posting_frequency']}")

    if 'title_patterns' in style:
        patterns = style['title_patterns']
        print(f"\n   📝 Паттерны заголовков:")
        print(f"      • Средняя длина: {patterns['avg_length']:.0f} символов")
        print(f"      • Используют числа: {patterns['uses_numbers']:.0f}%")
        print(f"      • Используют вопросы: {patterns['uses_questions']:.0f}%")

    # Performance scoring
    print("\n4️⃣ Ранжирование видео по эффективности...")
    ranked_videos = await analyzer.rank_videos_by_performance(channel_id, limit=5)

    print(f"\n   🏆 Топ-3 видео по performance score:")
    for i, video in enumerate(ranked_videos[:3], 1):
        print(f"   {i}. [{video['performance_score']:.1f}/100] {video['title']}")
        print(f"      👁  {analyzer._format_number(video['views'])} просмотров | "
              f"📊 {video['engagement_rate']:.2f}% engagement")

    # Подсчёт использованной квоты
    stats_after = await analyzer.get_api_usage_stats()
    quota_after = stats_after['used_today']
    quota_used = quota_after - quota_before

    print_section("ИТОГИ АНАЛИЗА", "✨")
    print(f"💰 Использовано квоты: {quota_used} единиц")
    print(f"⚡ Осталось на сегодня: {stats_after['remaining']} единиц")

    return quota_used


async def test_multilingual_analysis(analyzer: YouTubeAnalyzerAdvanced, channel_url: str):
    """Мультиязычный анализ"""
    print_section("МУЛЬТИЯЗЫЧНЫЙ АНАЛИЗ", "🌍")

    channel_info = await analyzer.get_channel_info(channel_url)
    channel_id = channel_info['id']

    stats_before = await analyzer.get_api_usage_stats()
    quota_before = stats_before['used_today']

    # Анализ
    result = await analyzer.analyze_channel_multilingual(
        channel_id,
        source_language='auto',
        target_language='ru'
    )

    print(f"\n🔍 Определённый язык: {result['language_name']} ({result['detected_language']})")
    print(f"🎯 Целевой рынок: Русский (ru)")
    print(f"🔄 Требуется перевод: {'Да' if result['translation_needed'] else 'Нет'}")

    print(f"\n📊 Базовая статистика:")
    print(f"   • Название: {result['channel_info']['title']}")
    print(f"   • Подписчики: {analyzer._format_number(result['channel_info']['subscribers'])}")

    print(f"\n🔥 Темы контента:")
    for i, theme in enumerate(result['content_themes'][:5], 1):
        print(f"   {i}. {theme}")

    print(f"\n💡 Советы по адаптации:")
    for suggestion in result['adaptation_suggestions']:
        print(f"   • {suggestion}")

    if result['translated_titles']:
        print(f"\n📝 Топ-5 заголовков:")
        for i, title in enumerate(result['translated_titles'][:5], 1):
            print(f"   {i}. {title}")

    stats_after = await analyzer.get_api_usage_stats()
    quota_used = stats_after['used_today'] - quota_before

    print(f"\n💰 Использовано квоты: {quota_used} единиц")


async def test_niche_search(analyzer: YouTubeAnalyzerAdvanced, topic: str = "programming tutorials"):
    """Поиск низкоконкурентных ниш"""
    print_section("ПОИСК НИЗКОКОНКУРЕНТНЫХ НИШ", "🔍")
    print("⚠️  ВНИМАНИЕ: Это дорогая операция (~200-300 единиц API)!")

    # Проверяем квоту
    stats = await analyzer.get_api_usage_stats()
    if stats['remaining'] < 300:
        print(f"❌ Недостаточно квоты! Осталось {stats['remaining']} единиц, требуется ~300")
        return

    print(f"✅ Квоты достаточно. Начинаем поиск по теме: '{topic}'...\n")

    stats_before = await analyzer.get_api_usage_stats()
    quota_before = stats_before['used_today']

    try:
        niches = await analyzer.find_underserved_niches(
            broad_topic=topic,
            min_views=10000,
            max_competition=100
        )

        print(f"🎯 Найдено {len(niches)} перспективных ниш:\n")

        for i, niche in enumerate(niches[:5], 1):
            print(f"{i}. {niche['niche']}")
            print(f"   📊 Средние просмотры: {analyzer._format_number(niche['avg_views'])}")
            print(f"   🏆 Конкуренция: {niche['competition_level']}")
            print(f"   {'✅ РЕКОМЕНДУЕТСЯ' if niche['recommended'] else '💡 Рассмотрите'}")

            if niche['example_channels']:
                example = niche['example_channels'][0]
                print(f"   📺 Пример: {example['title']} "
                      f"({analyzer._format_number(example['subscribers'])} подписчиков)")
            print()

    except Exception as e:
        print(f"❌ Ошибка: {str(e)}")

    stats_after = await analyzer.get_api_usage_stats()
    quota_used = stats_after['used_today'] - quota_before

    print(f"💰 Использовано квоты: {quota_used} единиц")


async def test_batch_analysis(analyzer: YouTubeAnalyzerAdvanced, channel_urls: list):
    """Пакетный анализ нескольких каналов"""
    print_section("ПАКЕТНЫЙ АНАЛИЗ КАНАЛОВ", "⚡")

    # Получаем IDs каналов
    channel_ids = []
    for url in channel_urls:
        try:
            info = await analyzer.get_channel_info(url)
            channel_ids.append(info['id'])
        except:
            print(f"⚠️  Не удалось получить ID для {url}")

    print(f"📋 Анализируем {len(channel_ids)} каналов...\n")

    stats_before = await analyzer.get_api_usage_stats()
    quota_before = stats_before['used_today']

    # Батчинг
    results = await analyzer.batch_analyze_channels(channel_ids)

    for i, result in enumerate(results, 1):
        if result['status'] == 'success':
            info = result['channel_info']
            style = result['style_summary']

            print(f"{i}. ✅ {info['title']}")
            print(f"   👥 Подписчики: {analyzer._format_number(info['subscriber_count'])}")
            print(f"   📊 Средние просмотры: {analyzer._format_number(style['avg_views'])}")
            print(f"   📅 Частота: {style['posting_frequency']}")
        else:
            print(f"{i}. ❌ Ошибка: {result['error']}")
        print()

    stats_after = await analyzer.get_api_usage_stats()
    quota_used = stats_after['used_today'] - quota_before
    quota_per_channel = quota_used / len(channel_ids) if channel_ids else 0

    print(f"💰 Всего использовано: {quota_used} единиц")
    print(f"📊 В среднем на канал: {quota_per_channel:.1f} единиц")
    print(f"💡 Экономия ~40% благодаря кэшированию и батчингу!")


async def main():
    """Главная функция"""
    # Парсинг аргументов
    parser = argparse.ArgumentParser(description='Advanced YouTube Analyzer Test')
    parser.add_argument('channel_url', nargs='?', help='URL канала для анализа')
    parser.add_argument('--mode', choices=['full', 'multilang', 'performance', 'niches', 'batch', 'quota'],
                       default='full', help='Режим анализа')
    parser.add_argument('--topic', default='programming tutorials', help='Тема для поиска ниш')

    args = parser.parse_args()

    # Загрузка API ключа
    load_dotenv()
    api_key = os.getenv('YOUTUBE_API_KEY')

    if not api_key or api_key == 'your_youtube_api_key_here':
        print("❌ ОШИБКА: YouTube API ключ не найден в .env файле")
        sys.exit(1)

    try:
        # Инициализация анализатора
        print("🚀 Инициализация Advanced YouTube Analyzer...")
        analyzer = YouTubeAnalyzerAdvanced(
            api_key=api_key,
            cache_ttl=3600,  # 1 час
            daily_quota_limit=10000
        )

        print("=" * 80)
        print("  🎬 YouTube Advanced Analyzer - Демонстрация возможностей")
        print("=" * 80)

        # Режим: только статистика квоты
        if args.mode == 'quota':
            stats = await analyzer.get_api_usage_stats()
            print_quota_stats(stats)
            return

        # Проверка URL для других режимов
        if not args.channel_url and args.mode != 'quota':
            print("❌ ОШИБКА: Укажите URL канала")
            parser.print_help()
            sys.exit(1)

        # Выполнение анализа в зависимости от режима
        if args.mode == 'full':
            await test_full_analysis(analyzer, args.channel_url)

        elif args.mode == 'multilang':
            await test_multilingual_analysis(analyzer, args.channel_url)

        elif args.mode == 'niches':
            await test_niche_search(analyzer, args.topic)

        elif args.mode == 'batch':
            # Для демонстрации используем один канал 3 раза
            channels = [args.channel_url] * 3
            await test_batch_analysis(analyzer, channels)

        # Финальная статистика
        print_section("ФИНАЛЬНАЯ СТАТИСТИКА", "📊")
        final_stats = await analyzer.get_api_usage_stats()
        print(f"💰 Всего использовано сегодня: {final_stats['used_today']} единиц")
        print(f"⚡ Осталось: {final_stats['remaining']} единиц")
        print(f"📊 Использовано: {final_stats['percentage_used']:.1f}%")

    except InvalidAPIKeyError as e:
        print(f"\n❌ ОШИБКА: {str(e)}")
    except ChannelNotFoundError as e:
        print(f"\n❌ ОШИБКА: {str(e)}")
    except QuotaExceededError as e:
        print(f"\n🚨 ОШИБКА КВОТЫ: {str(e)}")
    except Exception as e:
        print(f"\n❌ НЕОЖИДАННАЯ ОШИБКА: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
