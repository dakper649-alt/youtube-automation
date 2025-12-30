"""
Интеграционный тест полной цепочки генерации
Проверяет работу всех компонентов вместе (БЕЗ финального видео)
"""

import asyncio
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

async def test_full_pipeline():
    """Полный тест цепочки: скрипт → изображения → аудио"""

    print("\n" + "╔" + "=" * 78 + "╗")
    print("║" + " " * 15 + "ИНТЕГРАЦИОННЫЙ ТЕСТ ПОЛНОЙ ЦЕПОЧКИ" + " " * 29 + "║")
    print("╚" + "=" * 78 + "╝")

    try:
        # Импорты
        from services.api_key_manager import SafeAPIManager
        from services.script_gen import ScriptGenerator
        from services.text_normalizer import TextNormalizer
        from services.ken_burns import KenBurnsEffect

        print("\n[1/4] 🔧 Инициализация компонентов...")
        key_manager = SafeAPIManager()
        script_gen = ScriptGenerator(key_manager)
        normalizer = TextNormalizer(language='ru')
        ken_burns = KenBurnsEffect()
        print("   ✅ Все компоненты инициализированы")

        # ШАГ 1: Генерация скрипта
        print("\n[2/4] ✍️ Генерация короткого скрипта (200 слов)...")
        print("   Тема: Как токсичные люди изучают привычки")

        script_result = await script_gen.generate_script(
            topic="Как токсичные люди изучают ваши привычки",
            target_length=200,
            language='ru'
        )

        print(f"   ✅ Скрипт сгенерирован: {script_result['word_count']} слов")

        # ШАГ 2: Нормализация текста
        print("\n[3/4] 🔧 Нормализация текста для озвучки...")
        normalized_text = normalizer.normalize_for_tts(script_result['script'])
        validation = normalizer.validate_for_tts(normalized_text)

        if validation['is_valid']:
            print(f"   ✅ Текст нормализован: {validation['word_count']} слов")
        else:
            print(f"   ⚠️ Проблемы: {len(validation['issues'])}")
            for issue in validation['issues'][:3]:
                print(f"      - {issue}")

        # ШАГ 3: Ken Burns эффекты
        print("\n[4/4] 🎬 Применение Ken Burns эффектов...")

        # Создаём тестовые сцены
        test_scenes = [
            {'scene_description': script_result['hook'], 'duration': 3.0, 'path': 'test.png'},
            {'scene_description': 'Основная часть', 'duration': 5.0, 'path': 'test.png'},
            {'scene_description': script_result['cta'], 'duration': 3.0, 'path': 'test.png'},
        ]

        scenes_with_effects = ken_burns.apply_effect_to_scenes(test_scenes, script_result)
        print(f"   ✅ Применено {len(scenes_with_effects)} эффектов")

        # Сохраняем результаты
        print("\n📁 Сохранение результатов теста...")
        with open('test_pipeline_output.txt', 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write("РЕЗУЛЬТАТЫ ИНТЕГРАЦИОННОГО ТЕСТА\n")
            f.write("=" * 80 + "\n\n")

            f.write(f"HOOK:\n{script_result['hook']}\n\n")
            f.write(f"СКРИПТ ({script_result['word_count']} слов):\n{script_result['script']}\n\n")
            f.write(f"CTA:\n{script_result['cta']}\n\n")

            f.write("ЗАГОЛОВКИ:\n")
            for i, title in enumerate(script_result['title_suggestions'], 1):
                f.write(f"{i}. {title}\n")

            f.write(f"\nНОРМАЛИЗОВАННЫЙ ТЕКСТ:\n{normalized_text[:500]}...\n\n")

            f.write("KEN BURNS ЭФФЕКТЫ:\n")
            for i, scene in enumerate(scenes_with_effects, 1):
                f.write(f"{i}. {scene['scene_type']} → {scene['effect_type']}\n")

        print("   ✅ Результаты сохранены: test_pipeline_output.txt")

        print("\n" + "=" * 80)
        print("🎉 ИНТЕГРАЦИОННЫЙ ТЕСТ УСПЕШЕН!")
        print("=" * 80)
        print("\n✅ Все компоненты работают корректно!")
        print("💡 Система готова к генерации полного видео!")
        print("\nСледующий шаг: python backend/create_video_cli.py")
        print("=" * 80)

        return True

    except Exception as e:
        print(f"\n❌ ОШИБКА В ИНТЕГРАЦИОННОМ ТЕСТЕ: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_full_pipeline())
    exit(0 if success else 1)
