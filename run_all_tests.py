"""
Мастер-скрипт: запускает все тесты последовательно
"""

import subprocess
import sys

def run_test(test_name, command):
    """Запускает тест и возвращает результат"""
    print(f"\n{'=' * 80}")
    print(f"🧪 ЗАПУСК: {test_name}")
    print(f"{'=' * 80}\n")

    result = subprocess.run(command, shell=True)
    return result.returncode == 0

def main():
    print("\n╔" + "=" * 78 + "╗")
    print("║" + " " * 25 + "ПОЛНОЕ ТЕСТИРОВАНИЕ СИСТЕМЫ" + " " * 25 + "║")
    print("╚" + "=" * 78 + "╝")

    tests = [
        ("Юнит-тесты модулей", "python tests/test_modules.py"),
        ("Интеграционный тест", "python tests/test_full_pipeline.py"),
    ]

    results = {}

    for test_name, command in tests:
        results[test_name] = run_test(test_name, command)

    # Итоговый отчёт
    print("\n" + "=" * 80)
    print("ФИНАЛЬНЫЙ ОТЧЁТ:")
    print("=" * 80)

    for test_name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"   {test_name:30s} {status}")

    total_passed = sum(results.values())
    total_tests = len(results)

    print(f"\nВсего: {total_passed}/{total_tests} групп тестов пройдено")

    if total_passed == total_tests:
        print("\n" + "=" * 80)
        print("🎉 ВСЕ ТЕСТЫ УСПЕШНО ПРОЙДЕНЫ!")
        print("=" * 80)
        print("\n✅ Система полностью готова к работе!")
        print("\n📝 Следующие шаги:")
        print("   1. python backend/create_video_cli.py  - создать одно видео")
        print("   2. python backend/batch_create.py      - массовая генерация")
        print("=" * 80)
        return 0
    else:
        print(f"\n⚠️ {total_tests - total_passed} групп тестов провалено")
        print("Проверьте ошибки выше и исправьте проблемы.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
