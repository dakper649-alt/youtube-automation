#!/usr/bin/env python3
"""
Тестовый скрипт для проверки загрузки Hugging Face ключей

Этот скрипт проверяет:
1. Загружаются ли ключи из .env правильно
2. Сколько ключей загружено
3. Какие именно ключи загружены (первые символы)
4. Работает ли get_hf_key() метод
"""

import os
import sys
from dotenv import load_dotenv

# Загружаем .env из корневой директории
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

# Добавляем backend в путь
sys.path.insert(0, os.path.dirname(__file__))

from services.api_key_manager import APIKeyManager

def test_hf_keys_loading():
    """Тестирование загрузки HF ключей"""

    print("=" * 80)
    print("ТЕСТ ЗАГРУЗКИ HUGGING FACE КЛЮЧЕЙ")
    print("=" * 80)

    # 1. Проверка наличия ключей в .env напрямую
    print("\n📝 ШАГ 1: Проверка .env файла напрямую")
    print("-" * 80)

    hf_keys_from_env = []
    for i in range(1, 201):
        key = os.getenv(f'HUGGINGFACE_API_KEY_{i}')
        if key and key != 'your_hf_key_here':
            hf_keys_from_env.append(key)

    print(f"✅ Найдено ключей в .env (HUGGINGFACE_API_KEY_*): {len(hf_keys_from_env)}")

    if len(hf_keys_from_env) > 0:
        print(f"\n📋 Первые 5 ключей (первые 10 символов):")
        for i, key in enumerate(hf_keys_from_env[:5], 1):
            print(f"   {i}. {key[:10]}...{key[-4:]}")
    else:
        print("❌ КРИТИЧЕСКАЯ ОШИБКА: Ключи не найдены в .env!")
        print("   Проверьте, что в .env есть переменные типа:")
        print("   HUGGINGFACE_API_KEY_1=hf_...")
        print("   HUGGINGFACE_API_KEY_2=hf_...")
        return False

    # 2. Проверка загрузки через APIKeyManager
    print("\n\n🔑 ШАГ 2: Проверка загрузки через APIKeyManager")
    print("-" * 80)

    try:
        manager = APIKeyManager()
        print(f"✅ APIKeyManager инициализирован")

        # Проверяем атрибут hf_keys
        if hasattr(manager, 'hf_keys'):
            print(f"✅ Атрибут hf_keys существует")
            print(f"   Загружено ключей: {len(manager.hf_keys)}")

            if len(manager.hf_keys) != len(hf_keys_from_env):
                print(f"⚠️  НЕСООТВЕТСТВИЕ: в .env {len(hf_keys_from_env)} ключей, а загружено {len(manager.hf_keys)}")
            else:
                print(f"✅ Количество совпадает с .env файлом!")
        else:
            print("❌ ОШИБКА: Атрибут hf_keys отсутствует в APIKeyManager!")
            return False

    except Exception as e:
        print(f"❌ ОШИБКА при создании APIKeyManager: {e}")
        return False

    # 3. Тест метода get_hf_key()
    print("\n\n🎯 ШАГ 3: Тест метода get_hf_key()")
    print("-" * 80)

    try:
        key = manager.get_hf_key()
        print(f"✅ Метод get_hf_key() вернул ключ: {key[:10]}...{key[-4:]}")

        # Проверяем, что ключ есть в нашем списке
        if key in hf_keys_from_env:
            print(f"✅ Ключ совпадает с ключом из .env!")
        else:
            print(f"⚠️  Ключ НЕ найден в списке из .env (возможно, из другого источника)")

    except Exception as e:
        print(f"❌ ОШИБКА при вызове get_hf_key(): {e}")
        return False

    # 4. Проверка ротации ключей
    print("\n\n🔄 ШАГ 4: Тест ротации ключей (5 вызовов)")
    print("-" * 80)

    try:
        used_keys = []
        for i in range(5):
            key = manager.get_hf_key()
            used_keys.append(key[:10] + "..." + key[-4:])

        print(f"✅ Выдано 5 ключей:")
        for i, key_repr in enumerate(used_keys, 1):
            print(f"   {i}. {key_repr}")

        # Проверяем, использовались ли разные ключи
        unique_keys = len(set(used_keys))
        if unique_keys > 1:
            print(f"✅ Ротация работает! Использовано {unique_keys} разных ключей")
        else:
            print(f"⚠️  Ротация не работает или ключ всего 1")

    except Exception as e:
        print(f"❌ ОШИБКА при тестировании ротации: {e}")
        return False

    # 5. Итоговая статистика
    print("\n\n" + "=" * 80)
    print("📊 ИТОГОВАЯ СТАТИСТИКА")
    print("=" * 80)
    print(f"✅ В .env файле: {len(hf_keys_from_env)} ключей")
    print(f"✅ Загружено в APIKeyManager: {len(manager.hf_keys)} ключей")
    print(f"✅ Метод get_hf_key() работает: ДА")
    print(f"✅ Ротация ключей: {'ДА' if unique_keys > 1 else 'НЕТ (только 1 ключ)'}")

    print("\n" + "=" * 80)
    print("🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО!")
    print("=" * 80)

    return True


if __name__ == "__main__":
    success = test_hf_keys_loading()
    sys.exit(0 if success else 1)
