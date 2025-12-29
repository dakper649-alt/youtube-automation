#!/usr/bin/env python3
"""
Тестирование полной системы YouTube автоматизации

Демонстрирует работу всего пайплайна:
1. Инициализация оркестратора
2. Анализ ниши
3. Создание видео от идеи до готового контента

Использование:
    python test_full_system.py
"""

import asyncio
import sys
from pathlib import Path

# Добавляем путь к родительской директории для импорта
sys.path.insert(0, str(Path(__file__).parent))

from main_orchestrator import YouTubeAutomationOrchestrator, YouTubeAutomationError


async def test_niche_analysis():
    """
    Тест анализа ниши

    Проверяет:
    - Поиск идей
    - Анализ трендов
    - Рекомендации
    """
    print("\n" + "🧪 " + "=" * 68)
    print("🧪 ТЕСТ 1: АНАЛИЗ НИШИ")
    print("🧪 " + "=" * 68)

    try:
        # Инициализация оркестратора
        orchestrator = YouTubeAutomationOrchestrator()

        # Анализируем нишу
        niche = "психология"
        report = await orchestrator.analyze_niche(niche)

        # Проверяем результаты
        assert report is not None, "Отчёт не должен быть пустым"
        assert 'top_ideas' in report, "Отчёт должен содержать top_ideas"
        assert 'seasonal_trends' in report, "Отчёт должен содержать seasonal_trends"
        assert len(report['top_ideas']) > 0, "Должны быть найдены идеи"

        print("\n✅ ТЕСТ ПРОЙДЕН: Анализ ниши работает корректно")
        return True

    except Exception as e:
        print(f"\n❌ ТЕСТ ПРОВАЛЕН: {e}")
        return False


async def test_video_creation():
    """
    Тест создания видео

    Проверяет:
    - Поиск идей
    - Генерацию скрипта
    - Создание промптов для изображений
    """
    print("\n" + "🧪 " + "=" * 68)
    print("🧪 ТЕСТ 2: СОЗДАНИЕ ВИДЕО")
    print("🧪 " + "=" * 68)

    try:
        # Инициализация оркестратора
        orchestrator = YouTubeAutomationOrchestrator()

        # Создаём 1 видео
        niche = "психология"
        num_videos = 1

        projects = await orchestrator.create_video_pipeline(
            niche=niche,
            num_videos=num_videos,
            analyze_competitors=True,
            video_length=800,  # Короткий скрипт для теста
            style='educational',
            tone='professional',
            language='ru',
            image_style='minimalist_stick_figure'
        )

        # Проверяем результаты
        assert len(projects) == num_videos, f"Должно быть создано {num_videos} видео"

        project = projects[0]
        assert project['status'] == 'completed', "Проект должен быть завершён успешно"
        assert project['idea'] is not None, "Проект должен содержать идею"
        assert project['script'] is not None, "Проект должен содержать скрипт"
        assert project['image_prompts'] is not None, "Проект должен содержать промпты"
        assert len(project['image_prompts']) > 0, "Должны быть промпты для изображений"

        # Проверяем структуру скрипта
        script = project['script']
        assert 'script' in script, "Скрипт должен содержать текст"
        assert 'word_count' in script, "Скрипт должен содержать количество слов"
        assert 'estimated_duration' in script, "Скрипт должен содержать примерную длительность"
        assert 'title_suggestions' in script, "Скрипт должен содержать варианты заголовков"
        assert 'hook' in script, "Скрипт должен содержать хук"
        assert 'cta' in script, "Скрипт должен содержать призыв к действию"

        print("\n✅ ТЕСТ ПРОЙДЕН: Создание видео работает корректно")

        # Сохраняем проект для проверки
        output_file = "test_video_project.json"
        orchestrator.save_project(project, output_file)
        print(f"\n💾 Тестовый проект сохранён в {output_file}")

        # Показываем детали проекта
        print("\n" + "=" * 70)
        print("📋 ДЕТАЛИ СОЗДАННОГО ПРОЕКТА")
        print("=" * 70)
        print(f"\n📌 Идея:")
        print(f"   Заголовок: {project['idea']['title']}")
        print(f"   Описание: {project['idea']['description']}")
        print(f"   Вирусный потенциал: {project['idea']['viral_score']}/100")
        print(f"   Аудитория: {project['idea']['target_audience']}")

        print(f"\n📝 Скрипт:")
        print(f"   Слов: {script['word_count']}")
        print(f"   Примерная длительность: {script['estimated_duration']} сек")
        print(f"   Варианты заголовков: {len(script['title_suggestions'])}")

        print(f"\n🖼️  Изображения:")
        print(f"   Промптов: {len(project['image_prompts'])}")

        print("\n" + "=" * 70)

        return True

    except Exception as e:
        print(f"\n❌ ТЕСТ ПРОВАЛЕН: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_api_key_rotation():
    """
    Тест ротации API ключей

    Проверяет:
    - Работу APIKeyManager
    - Статистику использования
    """
    print("\n" + "🧪 " + "=" * 68)
    print("🧪 ТЕСТ 3: РОТАЦИЯ API КЛЮЧЕЙ")
    print("🧪 " + "=" * 68)

    try:
        # Инициализация оркестратора
        orchestrator = YouTubeAutomationOrchestrator()

        # Получаем статистику до
        stats_before = orchestrator.api_key_manager.get_stats()

        print("\n📊 Статистика ДО тестов:")
        for service, data in stats_before.items():
            print(f"   {service}: {data['requests']} запросов")

        # Делаем несколько запросов
        gemini_key = orchestrator.api_key_manager.get_gemini_key()
        assert gemini_key is not None, "Gemini ключ должен быть получен"

        if orchestrator.api_key_manager.youtube_keys:
            youtube_key = orchestrator.api_key_manager.get_youtube_key()
            assert youtube_key is not None, "YouTube ключ должен быть получен"

        # Получаем статистику после
        stats_after = orchestrator.api_key_manager.get_stats()

        print("\n📊 Статистика ПОСЛЕ тестов:")
        for service, data in stats_after.items():
            print(f"   {service}: {data['requests']} запросов")

        # Проверяем, что счётчики увеличились
        assert stats_after['gemini']['requests'] > stats_before['gemini']['requests'], \
            "Счётчик Gemini должен увеличиться"

        print("\n✅ ТЕСТ ПРОЙДЕН: Ротация API ключей работает корректно")
        return True

    except Exception as e:
        print(f"\n❌ ТЕСТ ПРОВАЛЕН: {e}")
        return False


async def main():
    """
    Главная функция для запуска всех тестов
    """
    print("\n" + "=" * 70)
    print("🚀 ТЕСТИРОВАНИЕ ПОЛНОЙ СИСТЕМЫ YOUTUBE АВТОМАТИЗАЦИИ")
    print("=" * 70)

    results = []

    # Запускаем тесты
    try:
        # Тест 1: Анализ ниши
        result1 = await test_niche_analysis()
        results.append(("Анализ ниши", result1))

        # Тест 2: Создание видео
        result2 = await test_video_creation()
        results.append(("Создание видео", result2))

        # Тест 3: Ротация API ключей
        result3 = await test_api_key_rotation()
        results.append(("Ротация API ключей", result3))

    except KeyboardInterrupt:
        print("\n\n⚠️  Тестирование прервано пользователем")
        return

    # Итоги
    print("\n" + "=" * 70)
    print("📊 ИТОГОВЫЕ РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ")
    print("=" * 70)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"   {status} - {test_name}")

    print()
    print(f"Пройдено тестов: {passed}/{total}")

    if passed == total:
        print("\n🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО!")
        print()
        return 0
    else:
        print(f"\n⚠️  Не пройдено тестов: {total - passed}")
        print()
        return 1


if __name__ == "__main__":
    """
    Точка входа для запуска тестов
    """
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n⚠️  Программа прервана пользователем")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ КРИТИЧЕСКАЯ ОШИБКА: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
