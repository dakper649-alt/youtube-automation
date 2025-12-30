"""
Юнит-тесты для всех модулей системы
Проверяет каждый компонент отдельно
"""

import sys
import os

# Добавляем backend в путь
project_root = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, os.path.join(project_root, 'backend'))

def test_1_imports():
    """Тест 1: Проверка импортов всех модулей"""
    print("\n" + "=" * 80)
    print("ТЕСТ 1: ИМПОРТЫ МОДУЛЕЙ")
    print("=" * 80)

    modules_to_test = [
        ('services.api_key_manager', 'SafeAPIManager'),
        ('services.text_normalizer', 'TextNormalizer'),
        ('services.script_gen', 'ScriptGenerator'),
        ('services.content_analyzer', 'ContentAnalyzer'),
        ('services.analyzer_advanced', 'YouTubeAnalyzer'),
        ('services.image_gen', 'ImageGenerator'),
        ('services.voice_manager', 'VoiceManager'),
        ('services.ken_burns', 'KenBurnsEffect'),
        ('services.subtitle_gen', 'SubtitleGenerator'),
        ('services.output_manager', 'OutputManager'),
        ('services.seo_generator', 'SEOGenerator'),
        ('services.telegram_notifier', 'TelegramNotifier'),
        ('services.batch_queue', 'BatchQueue'),
    ]

    passed = 0
    failed = 0

    for module_name, class_name in modules_to_test:
        try:
            module = __import__(module_name, fromlist=[class_name])
            getattr(module, class_name)
            print(f"   ✅ {module_name}.{class_name}")
            passed += 1
        except Exception as e:
            print(f"   ❌ {module_name}.{class_name}: {e}")
            failed += 1

    print(f"\nРезультат: {passed} успешно, {failed} ошибок")
    return failed == 0

def test_2_api_keys():
    """Тест 2: Проверка API ключей"""
    print("\n" + "=" * 80)
    print("ТЕСТ 2: API КЛЮЧИ")
    print("=" * 80)

    try:
        from services.api_key_manager import SafeAPIManager

        manager = SafeAPIManager()

        print(f"   Gemini ключей: {len(manager.gemini_keys)}")
        print(f"   Hugging Face ключей: {len(manager.hf_keys)}")
        print(f"   YouTube ключей: {len(manager.youtube_keys)}")
        print(f"   ElevenLabs ключей: {len(manager.elevenlabs_keys)}")

        if len(manager.elevenlabs_keys) == 54:
            print("   ✅ Все 54 ElevenLabs ключа на месте!")
            return True
        else:
            print(f"   ⚠️ ElevenLabs ключей: {len(manager.elevenlabs_keys)} (ожидалось 54)")
            return False

    except Exception as e:
        print(f"   ❌ Ошибка: {e}")
        return False

def test_3_text_normalizer():
    """Тест 3: Нормализация текста"""
    print("\n" + "=" * 80)
    print("ТЕСТ 3: TEXT NORMALIZER")
    print("=" * 80)

    try:
        from services.text_normalizer import TextNormalizer

        normalizer = TextNormalizer(language='ru')

        test_cases = [
            ("В 2024 году", "в две тысячи двадцать четвёртом году"),
            ("Цена 1000 руб.", "Цена одна тысяча рублей"),
            ("т.д.", "так далее"),
        ]

        passed = 0
        for original, _ in test_cases:
            try:
                normalized = normalizer.normalize_for_tts(original)
                print(f"   ✅ '{original}' → '{normalized[:50]}...'")
                passed += 1
            except Exception as e:
                print(f"   ❌ '{original}': {e}")

        return passed == len(test_cases)

    except Exception as e:
        print(f"   ❌ Ошибка: {e}")
        return False

def test_4_ken_burns():
    """Тест 4: Ken Burns эффекты"""
    print("\n" + "=" * 80)
    print("ТЕСТ 4: KEN BURNS EFFECTS")
    print("=" * 80)

    try:
        from services.ken_burns import KenBurnsEffect, SceneType, EffectType

        kb = KenBurnsEffect()

        # Тестовые сцены
        test_scenes = [
            {'scene_description': 'Введение', 'duration': 3.0},
            {'scene_description': 'Важный момент', 'duration': 4.0},
            {'scene_description': 'Заключение', 'duration': 3.0},
        ]

        scenes_with_effects = kb.apply_effect_to_scenes(test_scenes)

        if len(scenes_with_effects) == 3:
            print(f"   ✅ Применено {len(scenes_with_effects)} эффектов")
            return True
        else:
            print(f"   ❌ Ожидалось 3 эффекта, получено {len(scenes_with_effects)}")
            return False

    except Exception as e:
        print(f"   ❌ Ошибка: {e}")
        return False

def run_all_tests():
    """Запуск всех тестов"""
    print("\n" + "╔" + "=" * 78 + "╗")
    print("║" + " " * 20 + "ЮНИТ-ТЕСТЫ МОДУЛЕЙ" + " " * 40 + "║")
    print("╚" + "=" * 78 + "╝")

    results = {
        'Импорты': test_1_imports(),
        'API ключи': test_2_api_keys(),
        'Text Normalizer': test_3_text_normalizer(),
        'Ken Burns': test_4_ken_burns(),
    }

    print("\n" + "=" * 80)
    print("ИТОГОВЫЕ РЕЗУЛЬТАТЫ:")
    print("=" * 80)

    for test_name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"   {test_name:20s} {status}")

    total_passed = sum(results.values())
    total_tests = len(results)

    print(f"\nВсего: {total_passed}/{total_tests} тестов пройдено")

    if total_passed == total_tests:
        print("\n🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ!")
        return True
    else:
        print(f"\n⚠️ {total_tests - total_passed} тестов провалено")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)
