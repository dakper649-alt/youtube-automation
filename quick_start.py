#!/usr/bin/env python3
"""
🚀 QUICK START - Быстрый тест системы (5 минут)
Проверяет работу всех ключевых компонентов БЕЗ генерации видео
"""

import asyncio
import sys
import os

# Добавляем backend в путь
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

async def quick_start():
    print("\n" + "╔" + "=" * 78 + "╗")
    print("║" + " " * 20 + "🚀 QUICK START - ТЕСТ СИСТЕМЫ" + " " * 28 + "║")
    print("╚" + "=" * 78 + "╝")

    print("\nЭтот тест проверит:")
    print("  ✅ Импорты всех модулей")
    print("  ✅ API ключи (54 ElevenLabs)")
    print("  ✅ Генерацию скрипта через Gemini")
    print("  ✅ Нормализацию текста для TTS")
    print("  ✅ Ken Burns эффекты")
    print("\n⏱️ Ожидаемое время: ~5 минут\n")

    try:
        # ШАГ 1: Импорты
        print("[1/5] 📦 Проверка импортов...")
        from services.api_key_manager import SafeAPIManager
        from services.script_gen import ScriptGenerator
        from services.text_normalizer import TextNormalizer
        from services.ken_burns import KenBurnsEffect
        print("      ✅ Все модули импортируются")

        # ШАГ 2: API ключи
        print("\n[2/5] 🔑 Проверка API ключей...")
        key_manager = SafeAPIManager()
        print(f"      ✅ ElevenLabs: {len(key_manager.elevenlabs_keys)} ключей")
        print(f"      ✅ Gemini: {len(key_manager.gemini_keys)} ключей")
        print(f"      ✅ Hugging Face: {len(key_manager.hf_keys)} ключей")

        # ШАГ 3: Генерация скрипта
        print("\n[3/5] ✍️ Генерация тестового скрипта...")
        print("      Тема: Как токсичные люди изучают привычки")
        print("      Длина: ~200 слов")

        script_gen = ScriptGenerator(key_manager)
        script_result = await script_gen.generate_script(
            topic="Как токсичные люди изучают ваши привычки",
            target_length=200,
            language='ru'
        )

        print(f"      ✅ Скрипт сгенерирован: {script_result['word_count']} слов")

        # ШАГ 4: Нормализация
        print("\n[4/5] 🔧 Нормализация текста...")
        normalizer = TextNormalizer(language='ru')
        normalized = normalizer.normalize_for_tts(script_result['script'])
        print(f"      ✅ Текст нормализован")

        # ШАГ 5: Ken Burns
        print("\n[5/5] 🎬 Проверка Ken Burns эффектов...")
        ken_burns = KenBurnsEffect()
        test_scenes = [
            {'scene_description': 'Тестовая сцена', 'duration': 3.0}
        ]
        scenes_with_effects = ken_burns.apply_effect_to_scenes(test_scenes)
        print(f"      ✅ Эффекты применены: {len(scenes_with_effects)}")

        # Сохранение результата
        print("\n📁 Сохранение результатов...")
        output_file = 'quick_start_result.txt'
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write("QUICK START - РЕЗУЛЬТАТЫ ТЕСТА\n")
            f.write("=" * 80 + "\n\n")
            f.write(f"HOOK:\n{script_result['hook']}\n\n")
            f.write(f"СКРИПТ ({script_result['word_count']} слов):\n")
            f.write(f"{script_result['script']}\n\n")
            f.write(f"CTA:\n{script_result['cta']}\n\n")
            f.write("ЗАГОЛОВКИ:\n")
            for i, title in enumerate(script_result['title_suggestions'], 1):
                f.write(f"{i}. {title}\n")

        print(f"      ✅ Результаты: {output_file}")

        # Успех!
        print("\n" + "=" * 80)
        print("🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО!")
        print("=" * 80)
        print("\n✅ Система работает отлично!")
        print("\n📝 Следующие шаги:")
        print("   1. Проверь файл:", output_file)
        print("   2. Запусти полную генерацию:")
        print("      python backend/create_video_cli.py")
        print("\n⏱️ Полное видео займёт ~40-60 минут")
        print("=" * 80)

        return True

    except Exception as e:
        print(f"\n❌ ОШИБКА: {e}")
        import traceback
        traceback.print_exc()

        print("\n💡 Проверь:")
        print("   - Установлены ли зависимости: pip install -r requirements.txt")
        print("   - Активирован ли venv: source venv/bin/activate")
        print("   - Есть ли файл .env с API ключами")

        return False

if __name__ == "__main__":
    success = asyncio.run(quick_start())
    sys.exit(0 if success else 1)
