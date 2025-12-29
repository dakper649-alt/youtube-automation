#!/usr/bin/env python3
"""
Примеры использования YouTube Automation System

Демонстрирует различные сценарии использования:
1. Быстрое создание одного видео
2. Анализ ниши перед созданием контента
3. Пакетное создание нескольких видео
4. Работа с отдельными компонентами

Использование:
    python example_usage.py
"""

import asyncio
import sys
from pathlib import Path

# Добавляем путь к родительской директории для импорта
sys.path.insert(0, str(Path(__file__).parent))

from main_orchestrator import YouTubeAutomationOrchestrator
from services.api_key_manager import APIKeyManager
from services.content_analyzer import ContentAnalyzer
from services.script_gen import ScriptGenerator


async def example_1_quick_video():
    """
    ПРИМЕР 1: Быстрое создание одного видео

    Самый простой способ создать видео:
    - Указываете нишу
    - Система сама находит лучшую идею
    - Генерирует скрипт и промпты
    """
    print("\n" + "=" * 70)
    print("📹 ПРИМЕР 1: Быстрое создание одного видео")
    print("=" * 70)

    # Инициализация
    orchestrator = YouTubeAutomationOrchestrator()

    # Создание видео
    projects = await orchestrator.create_video_pipeline(
        niche="психология",           # Ниша
        num_videos=1,                 # 1 видео
        video_length=800,             # Короткий скрипт для примера
        style='educational',          # Образовательный стиль
        tone='professional',          # Профессиональный тон
        language='ru'                 # Русский язык
    )

    # Результат
    project = projects[0]
    print("\n🎉 Видео готово!")
    print(f"   Заголовок: {project['idea']['title']}")
    print(f"   Вирусный потенциал: {project['idea']['viral_score']}/100")
    print(f"   Слов в скрипте: {project['script']['word_count']}")
    print(f"   Промптов для изображений: {len(project['image_prompts'])}")

    # Сохранение
    orchestrator.save_project(project, "example_video.json")
    print(f"\n💾 Проект сохранён в example_video.json")


async def example_2_analyze_first():
    """
    ПРИМЕР 2: Анализ ниши перед созданием

    Сначала анализируем нишу, смотрим тренды,
    затем создаём видео на основе анализа
    """
    print("\n" + "=" * 70)
    print("🔍 ПРИМЕР 2: Анализ ниши перед созданием")
    print("=" * 70)

    orchestrator = YouTubeAutomationOrchestrator()

    # Шаг 1: Анализ ниши
    print("\n📊 Шаг 1: Анализируем нишу...")
    report = await orchestrator.analyze_niche("саморазвитие")

    # Показываем результаты анализа
    print("\n📈 Результаты анализа:")
    print(f"   Лучшая идея: {report['recommendations']['best_idea']['title']}")
    print(f"   Вирусный потенциал: {report['recommendations']['best_idea']['viral_score']}/100")
    print(f"   Лучшее время публикации: {report['recommendations']['best_time_to_publish']}")
    print(f"   Текущие тренды: {', '.join(report['seasonal_trends']['current_trends'][:3])}")

    # Шаг 2: Создание видео на основе анализа
    print("\n📹 Шаг 2: Создаём видео на основе анализа...")

    # Берём лучшую идею из анализа
    best_idea = report['recommendations']['best_idea']

    # Создаём видео с этой идеей
    projects = await orchestrator.create_video_pipeline(
        niche="саморазвитие",
        num_videos=1,
        video_length=1000,
        style='educational',
        tone='professional',
        language='ru'
    )

    print("\n✅ Видео создано на основе анализа!")


async def example_3_batch_creation():
    """
    ПРИМЕР 3: Пакетное создание нескольких видео

    Создаём несколько видео за один раз
    для контент-плана на неделю
    """
    print("\n" + "=" * 70)
    print("📚 ПРИМЕР 3: Пакетное создание 3 видео")
    print("=" * 70)

    orchestrator = YouTubeAutomationOrchestrator()

    # Создаём 3 видео
    projects = await orchestrator.create_video_pipeline(
        niche="productivity",
        num_videos=3,               # 3 видео
        video_length=600,           # Короткие для примера
        style='entertaining',       # Развлекательный стиль
        tone='casual',              # Разговорный тон
        language='ru'
    )

    # Показываем все созданные видео
    print("\n📋 Созданные видео:")
    for i, project in enumerate(projects, 1):
        print(f"\n{i}. {project['idea']['title']}")
        print(f"   Вирусный потенциал: {project['idea']['viral_score']}/100")
        print(f"   Статус: {project['status']}")

        # Сохраняем каждое видео
        filename = f"batch_video_{i}.json"
        orchestrator.save_project(project, filename)
        print(f"   Сохранено в: {filename}")


async def example_4_components():
    """
    ПРИМЕР 4: Работа с отдельными компонентами

    Показывает как использовать отдельные части системы:
    - ContentAnalyzer для поиска идей
    - ScriptGenerator для генерации скриптов
    """
    print("\n" + "=" * 70)
    print("🧩 ПРИМЕР 4: Работа с отдельными компонентами")
    print("=" * 70)

    # Инициализация компонентов
    api_manager = APIKeyManager()

    # Компонент 1: Content Analyzer
    print("\n📊 Компонент 1: ContentAnalyzer")
    print("-" * 70)

    analyzer = ContentAnalyzer(api_manager)

    # Поиск идей
    ideas = await analyzer.find_best_video_ideas(
        niche="мотивация",
        num_ideas=5,
        analyze_competitors=True
    )

    print(f"Найдено идей: {len(ideas)}")
    print("\nТоп-3 идеи:")
    for i, idea in enumerate(ideas[:3], 1):
        print(f"{i}. {idea['title']}")
        print(f"   Вирусный потенциал: {idea['viral_score']}/100")

    # Компонент 2: Script Generator
    print("\n\n📝 Компонент 2: ScriptGenerator")
    print("-" * 70)

    gemini_key = api_manager.get_gemini_key()
    generator = ScriptGenerator(gemini_key, provider="gemini")

    # Генерация скрипта для лучшей идеи
    best_idea = ideas[0]
    print(f"Генерируем скрипт для: {best_idea['title']}")

    script = await generator.generate_script(
        topic=best_idea['title'],
        target_length=500,  # Короткий для примера
        language='ru',
        style='educational',
        tone='professional'
    )

    print(f"\n✅ Скрипт сгенерирован!")
    print(f"   Слов: {script['word_count']}")
    print(f"   Длительность: ~{script['estimated_duration']} секунд")
    print(f"\n📄 Превью скрипта:")
    print(script['script'][:200] + "...")

    # Промпты для изображений
    print("\n\n🖼️  Компонент 3: Генерация промптов для изображений")
    print("-" * 70)

    image_prompts = await generator.generate_image_prompts(
        script=script['script'],
        style='minimalist_stick_figure',
        images_per_minute=10
    )

    print(f"Сгенерировано {len(image_prompts)} промптов")
    print("\nПримеры промптов:")
    for i, prompt_data in enumerate(image_prompts[:2], 1):
        print(f"{i}. [{prompt_data['timestamp']}s] {prompt_data['prompt'][:60]}...")


async def example_5_custom_settings():
    """
    ПРИМЕР 5: Кастомные настройки

    Показывает различные настройки для разных типов контента
    """
    print("\n" + "=" * 70)
    print("⚙️  ПРИМЕР 5: Кастомные настройки")
    print("=" * 70)

    orchestrator = YouTubeAutomationOrchestrator()

    # Вариант 1: Короткое развлекательное видео
    print("\n🎪 Вариант 1: Короткое развлекательное видео (YouTube Shorts)")
    print("-" * 70)

    short_video = await orchestrator.create_video_pipeline(
        niche="лайфхаки",
        num_videos=1,
        video_length=200,           # Очень короткий скрипт
        style='entertaining',        # Развлекательный
        tone='humorous',            # Юмористический
        language='ru',
        image_style='cartoon'       # Мультяшный стиль
    )

    print(f"✅ Короткое видео создано: {short_video[0]['idea']['title']}")

    # Вариант 2: Длинное образовательное видео
    print("\n🎓 Вариант 2: Длинное образовательное видео")
    print("-" * 70)

    long_video = await orchestrator.create_video_pipeline(
        niche="наука",
        num_videos=1,
        video_length=2000,          # Длинный скрипт
        style='documentary',        # Документальный
        tone='professional',        # Профессиональный
        language='ru',
        image_style='cinematic_photography'  # Кинематографичный
    )

    print(f"✅ Длинное видео создано: {long_video[0]['idea']['title']}")


async def main():
    """
    Главная функция - выбор примера
    """
    print("\n" + "=" * 70)
    print("🎬 ПРИМЕРЫ ИСПОЛЬЗОВАНИЯ YOUTUBE AUTOMATION SYSTEM")
    print("=" * 70)
    print()
    print("Доступные примеры:")
    print("1. Быстрое создание одного видео")
    print("2. Анализ ниши перед созданием")
    print("3. Пакетное создание 3 видео")
    print("4. Работа с отдельными компонентами")
    print("5. Кастомные настройки")
    print("0. Запустить все примеры")
    print()

    try:
        choice = input("Выберите пример (0-5): ").strip()

        if choice == "1":
            await example_1_quick_video()
        elif choice == "2":
            await example_2_analyze_first()
        elif choice == "3":
            await example_3_batch_creation()
        elif choice == "4":
            await example_4_components()
        elif choice == "5":
            await example_5_custom_settings()
        elif choice == "0":
            # Запускаем все примеры
            await example_1_quick_video()
            await example_2_analyze_first()
            await example_3_batch_creation()
            await example_4_components()
            await example_5_custom_settings()
        else:
            print("❌ Неверный выбор")
            return

        print("\n" + "=" * 70)
        print("✅ ПРИМЕРЫ ВЫПОЛНЕНЫ УСПЕШНО!")
        print("=" * 70)
        print()

    except KeyboardInterrupt:
        print("\n\n⚠️  Прервано пользователем")
    except Exception as e:
        print(f"\n\n❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    """
    Точка входа
    """
    asyncio.run(main())
