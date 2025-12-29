#!/usr/bin/env python3
"""
Утилита для автоматической проверки API ключей Grok

Использование:
    python backend/utils/test_api_keys.py

Настройка:
    Добавьте в .env: GROK_KEYS_LIST=key1,key2,key3,...
"""

import asyncio
import os
import openai
from typing import List, Dict, Optional
from dotenv import load_dotenv

load_dotenv()

# Загружаем ключи из переменной окружения
keys_env = os.getenv('GROK_KEYS_LIST', '')
GROK_KEYS = [key.strip() for key in keys_env.split(',') if key.strip()]

# Если ключи не настроены, используем пустой список
if not GROK_KEYS:
    print("⚠️  GROK_KEYS_LIST не настроен в .env")
    print("💡 Добавьте в .env: GROK_KEYS_LIST=key1,key2,key3,...")
    GROK_KEYS = []


async def test_grok_key(api_key: str) -> Dict:
    """
    Тестирует один ключ Grok API

    Args:
        api_key: API ключ для проверки

    Returns:
        dict с результатом проверки:
            - key: API ключ
            - status: "working" или "failed"
            - response/error: ответ или ошибка
    """

    print(f"🔍 Проверяю ключ: {api_key[:20]}...")

    try:
        client = openai.OpenAI(
            api_key=api_key,
            base_url="https://api.x.ai/v1"
        )

        response = client.chat.completions.create(
            model="grok-beta",
            messages=[{"role": "user", "content": "Скажи 'привет'"}],
            max_tokens=10,
            timeout=10.0
        )

        result_text = response.choices[0].message.content
        print(f"✅ Ключ РАБОТАЕТ: {api_key[:20]}... → {result_text}")

        return {
            "key": api_key,
            "status": "working",
            "response": result_text
        }

    except openai.AuthenticationError as e:
        print(f"❌ Ключ НЕ ВАЛИДЕН: {api_key[:20]}... → Ошибка аутентификации")
        return {
            "key": api_key,
            "status": "failed",
            "error": "Authentication failed"
        }

    except openai.RateLimitError as e:
        print(f"⚠️  Ключ достиг лимита: {api_key[:20]}... → Rate limit")
        return {
            "key": api_key,
            "status": "rate_limited",
            "error": "Rate limit exceeded"
        }

    except Exception as e:
        error_msg = str(e)[:50]
        print(f"❌ Ключ НЕ работает: {api_key[:20]}... → {error_msg}")
        return {
            "key": api_key,
            "status": "failed",
            "error": str(e)
        }


async def find_working_grok_key() -> Optional[str]:
    """
    Проверяет все ключи Grok и возвращает первый рабочий

    Returns:
        str: Рабочий API ключ или None если ни один не работает
    """

    print("=" * 80)
    print("🔑 ПРОВЕРКА КЛЮЧЕЙ GROK API (X.AI)")
    print("=" * 80)
    print(f"Всего ключей для проверки: {len(GROK_KEYS)}\n")

    working_keys = []

    for i, key in enumerate(GROK_KEYS, 1):
        print(f"\n[{i}/{len(GROK_KEYS)}]")
        result = await test_grok_key(key)

        if result["status"] == "working":
            working_keys.append(key)

        # Небольшая задержка между проверками
        if i < len(GROK_KEYS):
            await asyncio.sleep(0.5)

    print("\n" + "=" * 80)

    if working_keys:
        print(f"✅ НАЙДЕНО РАБОЧИХ КЛЮЧЕЙ: {len(working_keys)}")
        print(f"\nПервый рабочий ключ: {working_keys[0]}")
        print("\n💡 Добавьте его в .env:")
        print(f"   GROK_API_KEY={working_keys[0]}")
        print("=" * 80)
        return working_keys[0]
    else:
        print("❌ НИ ОДИН КЛЮЧ GROK НЕ РАБОТАЕТ!")
        print("\n💡 Рекомендация: используйте Google Gemini API (бесплатно навсегда)")
        print("   Получите ключ: https://aistudio.google.com/")
        print("   Добавьте в .env: GOOGLE_API_KEY=your_key_here")
        print("=" * 80)
        return None


async def test_all_keys() -> Dict[str, List[str]]:
    """
    Тестирует все ключи и возвращает статистику

    Returns:
        dict: {
            "working": [список рабочих ключей],
            "failed": [список нерабочих ключей],
            "rate_limited": [список ключей с лимитом]
        }
    """

    print("=" * 80)
    print("🔍 ПОЛНАЯ ПРОВЕРКА ВСЕХ КЛЮЧЕЙ GROK")
    print("=" * 80)

    results = {
        "working": [],
        "failed": [],
        "rate_limited": []
    }

    for i, key in enumerate(GROK_KEYS, 1):
        print(f"\n[{i}/{len(GROK_KEYS)}]")
        result = await test_grok_key(key)

        if result["status"] == "working":
            results["working"].append(key)
        elif result["status"] == "rate_limited":
            results["rate_limited"].append(key)
        else:
            results["failed"].append(key)

        if i < len(GROK_KEYS):
            await asyncio.sleep(0.5)

    # Статистика
    print("\n" + "=" * 80)
    print("📊 РЕЗУЛЬТАТЫ:")
    print(f"   ✅ Рабочих: {len(results['working'])}")
    print(f"   ⚠️  С лимитом: {len(results['rate_limited'])}")
    print(f"   ❌ Нерабочих: {len(results['failed'])}")
    print("=" * 80)

    return results


if __name__ == "__main__":
    # Можно выбрать режим:
    # 1. Найти первый рабочий ключ (быстро)
    # 2. Проверить все ключи (полная статистика)

    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--all":
        # Полная проверка всех ключей
        asyncio.run(test_all_keys())
    else:
        # Быстрая проверка - первый рабочий
        asyncio.run(find_working_grok_key())
