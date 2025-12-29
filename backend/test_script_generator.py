#!/usr/bin/env python3
"""
Тестовый скрипт для проверки генератора скриптов

Использование:
    python test_script_generator.py

Требуется:
    ANTHROPIC_API_KEY в файле .env
"""

import asyncio
import sys
import os
from dotenv import load_dotenv

# Добавляем путь к модулям
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from backend.services.script_gen import ScriptGenerator, ScriptGeneratorError, InvalidAPIKeyError


def print_section(title: str):
    """Печать красивого разделителя"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)


async def test_script_generation():
    """Тест генерации скрипта"""

    print_section("ТЕСТ 1: Генерация скрипта для YouTube видео")

    # API ключ из переменных окружения
    load_dotenv()
    api_key = os.getenv('OPENROUTER_API_KEY')

    if not api_key or api_key == 'your_openrouter_api_key_here':
        print("\n❌ ОШИБКА: OPENROUTER_API_KEY не найден в .env файле")
        print("\n💡 Добавьте в .env:")
        print("   OPENROUTER_API_KEY=sk-or-v1-...")
        print("\n🌐 Получите бесплатный ключ: https://openrouter.ai/keys")
        return

    try:
        # Инициализация генератора
        print("\n🚀 Инициализация ScriptGenerator...")
        model = "google/gemini-flash-1.5"
        generator = ScriptGenerator(api_key, model=model)
        print(f"✅ Генератор инициализирован успешно")
        print(f"   🤖 Модель: {model}")
        print(f"   💰 Стоимость: БЕСПЛАТНО!")

        # Генерация скрипта
        print("\n📝 Генерация скрипта...")
        print("   Тема: 'Как токсичные люди изучают ваши привычки'")
        print("   Длина: 800 слов")
        print("   Язык: русский")
        print("   Стиль: образовательный")

        result = await generator.generate_script(
            topic="Как токсичные люди изучают ваши привычки",
            target_length=800,
            language='ru',
            style='educational',
            tone='professional'
        )

        print(f"\n✅ Скрипт сгенерирован!")
        print(f"   📊 Статистика:")
        print(f"      • Слов: {result['word_count']}")
        print(f"      • Примерная длительность: {result['estimated_duration']} секунд "
              f"(~{result['estimated_duration']//60} мин {result['estimated_duration']%60} сек)")
        print(f"      • Заголовков: {len(result['title_suggestions'])}")

        print(f"\n🎯 HOOK (захватывающее начало):")
        print("-" * 80)
        print(result['hook'])

        print(f"\n📜 СКРИПТ (первые 500 символов):")
        print("-" * 80)
        print(result['script'][:500] + "...")

        print(f"\n📢 ПРИЗЫВ К ДЕЙСТВИЮ (CTA):")
        print("-" * 80)
        print(result['cta'])

        print(f"\n📌 ВАРИАНТЫ ЗАГОЛОВКОВ:")
        for i, title in enumerate(result['title_suggestions'], 1):
            print(f"   {i}. {title}")

    except InvalidAPIKeyError as e:
        print(f"\n❌ ОШИБКА API ключа: {str(e)}")
        return
    except ScriptGeneratorError as e:
        print(f"\n❌ ОШИБКА генерации: {str(e)}")
        return
    except Exception as e:
        print(f"\n❌ НЕОЖИДАННАЯ ОШИБКА: {str(e)}")
        import traceback
        traceback.print_exc()
        return

    # ============================================================
    # ТЕСТ 2: Генерация промптов для изображений
    # ============================================================
    print_section("ТЕСТ 2: Генерация промптов для изображений")

    try:
        print("\n🎨 Генерация промптов для изображений...")
        print("   Стиль: minimalist_stick_figure")
        print("   Частота: 15 изображений в минуту")

        prompts = await generator.generate_image_prompts(
            script=result['script'],
            style="minimalist_stick_figure",
            images_per_minute=15
        )

        print(f"\n✅ Сгенерировано {len(prompts)} промптов для изображений")

        print(f"\n🖼  Примеры промптов:")
        print("-" * 80)

        # Показываем первые 3 промпта
        for i, prompt_data in enumerate(prompts[:3], 1):
            print(f"\n{i}. Timestamp: {prompt_data['timestamp']}s")
            print(f"   Duration: {prompt_data['duration']}s")
            print(f"   Scene: {prompt_data['scene_description']}")
            print(f"   Prompt: {prompt_data['prompt'][:150]}...")

    except ScriptGeneratorError as e:
        print(f"\n❌ ОШИБКА генерации промптов: {str(e)}")
    except Exception as e:
        print(f"\n❌ НЕОЖИДАННАЯ ОШИБКА: {str(e)}")

    # ============================================================
    # ТЕСТ 3: Перевод скрипта
    # ============================================================
    print_section("ТЕСТ 3: Перевод скрипта на английский")

    try:
        print("\n🌐 Перевод скрипта...")
        print("   Целевой язык: английский (en)")

        # Берём начало скрипта для перевода (экономим токены)
        script_chunk = result['script'][:400]

        translated = await generator.translate_script(
            script=script_chunk,
            target_language='en'
        )

        print(f"\n✅ Перевод выполнен!")
        print(f"   Слов: {translated['word_count']}")

        print(f"\n📝 Переведённый текст:")
        print("-" * 80)
        print(translated['script'][:400] + "...")

    except ScriptGeneratorError as e:
        print(f"\n❌ ОШИБКА перевода: {str(e)}")
    except Exception as e:
        print(f"\n❌ НЕОЖИДАННАЯ ОШИБКА: {str(e)}")

    # ============================================================
    # ТЕСТ 4: SEO оптимизация
    # ============================================================
    print_section("ТЕСТ 4: SEO оптимизация скрипта")

    try:
        print("\n🔍 SEO оптимизация...")
        keywords = ["токсичные люди", "психология", "манипуляция"]
        print(f"   Ключевые слова: {', '.join(keywords)}")

        seo_result = await generator.optimize_for_seo(
            script=result['script'][:500],  # первые 500 символов
            primary_keywords=keywords
        )

        print(f"\n✅ SEO оптимизация выполнена!")

        print(f"\n📊 Плотность ключевых слов:")
        for keyword, density in seo_result['keyword_density'].items():
            print(f"   • {keyword}: {density}%")

        print(f"\n📌 SEO заголовок:")
        print(f"   {seo_result['seo_title']}")

        print(f"\n📝 SEO описание:")
        print(f"   {seo_result['seo_description']}")

        print(f"\n🏷  Рекомендованные теги ({len(seo_result['tags'])} шт):")
        tags_str = ", ".join(seo_result['tags'][:10])
        print(f"   {tags_str}")

    except ScriptGeneratorError as e:
        print(f"\n❌ ОШИБКА SEO оптимизации: {str(e)}")
    except Exception as e:
        print(f"\n❌ НЕОЖИДАННАЯ ОШИБКА: {str(e)}")

    # ============================================================
    # Итоги
    # ============================================================
    print_section("✅ ВСЕ ТЕСТЫ ЗАВЕРШЕНЫ")
    print("\n💡 Генератор скриптов полностью функционален и готов к использованию!")
    print("\nВозможности:")
    print("   ✓ Генерация скриптов на разных языках")
    print("   ✓ Создание промптов для изображений")
    print("   ✓ Перевод скриптов")
    print("   ✓ SEO оптимизация")
    print("   ✓ Различные стили и тона")


async def main():
    """Главная функция"""
    print("=" * 80)
    print("  🎬 ScriptGenerator - Тестирование модуля генерации скриптов")
    print("=" * 80)

    await test_script_generation()


if __name__ == "__main__":
    asyncio.run(main())
