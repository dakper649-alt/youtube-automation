"""
Тестирование всех AI API
"""

import os
import sys
import asyncio
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

async def test_gemini():
    """Тест нового Gemini API"""
    print("\n" + "=" * 80)
    print("🧪 ТЕСТ: Google Gemini 2.0 Flash API (новая библиотека)")
    print("=" * 80)

    try:
        from google import genai
        from google.genai import types
        from services.api_key_manager import SafeAPIManager

        manager = SafeAPIManager()
        key = manager.get_gemini_key()

        if not key:
            print("❌ Нет Gemini ключей")
            return False

        print(f"🔑 Ключ: {key[:20]}...")

        client = genai.Client(api_key=key)

        print("⏱️ Генерация 50 слов...")
        import time
        start = time.time()

        response = client.models.generate_content(
            model='gemini-2.0-flash-exp',
            contents="Напиши короткий текст на 50 слов про психологию",
            config=types.GenerateContentConfig(
                temperature=0.9,
                max_output_tokens=200
            )
        )

        elapsed = time.time() - start

        print(f"✅ Готово за {elapsed:.1f} сек")
        print(f"📝 Текст: {response.text[:100]}...")
        return True

    except Exception as e:
        print(f"❌ ОШИБКА: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_openai():
    """Тест OpenAI API"""
    print("\n" + "=" * 80)
    print("🧪 ТЕСТ: OpenAI GPT-4o-mini API")
    print("=" * 80)

    try:
        from openai import OpenAI

        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            print("❌ Нет OPENAI_API_KEY в .env")
            print("💡 Добавь OPENAI_API_KEY=sk-... в файл .env")
            return False

        print(f"🔑 Ключ: {api_key[:20]}...")

        client = OpenAI(api_key=api_key)

        print("⏱️ Генерация 50 слов...")
        import time
        start = time.time()

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "user", "content": "Напиши короткий текст на 50 слов про психологию"}
            ],
            temperature=0.9,
            max_tokens=200
        )

        elapsed = time.time() - start

        print(f"✅ Готово за {elapsed:.1f} сек")
        print(f"📝 Текст: {response.choices[0].message.content[:100]}...")
        return True

    except Exception as e:
        print(f"❌ ОШИБКА: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    print("\n╔" + "=" * 78 + "╗")
    print("║" + " " * 25 + "ТЕСТИРОВАНИЕ AI API" + " " * 33 + "║")
    print("╚" + "=" * 78 + "╝")

    results = {
        'Gemini 2.0': await test_gemini(),
        'OpenAI GPT-4o-mini': await test_openai(),
    }

    print("\n" + "=" * 80)
    print("РЕЗУЛЬТАТЫ:")
    print("=" * 80)

    for api, passed in results.items():
        status = "✅ РАБОТАЕТ" if passed else "❌ НЕ РАБОТАЕТ"
        print(f"   {api:25s} {status}")

    if any(results.values()):
        print("\n✅ Хотя бы один API работает - система готова!")
        return 0
    else:
        print("\n❌ Ни один API не работает - проверьте ключи")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
