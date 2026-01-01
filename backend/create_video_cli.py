"""
Простая CLI команда для создания видео
Использование: python backend/create_video_cli.py
"""

import asyncio
from main_orchestrator import YouTubeAutomationOrchestrator


async def main():
    print("=" * 80)
    print("🎬 YOUTUBE VIDEO GENERATOR")
    print("=" * 80)

    # Выбор рендерера
    print("\n🎨 Выберите рендерер:")
    print("   1. Remotion (профессиональные эффекты, медленнее)")
    print("   2. MoviePy (базовые эффекты, быстрее)")

    renderer_choice = input("\n   Выбор (1/2, по умолчанию 1): ").strip() or "1"
    use_remotion = renderer_choice == "1"

    # Инициализация системы с выбранным рендерером
    system = YouTubeAutomationOrchestrator(use_remotion=use_remotion)

    # Примеры тем
    print("\n💡 Примеры тем:")
    print("1. Как токсичные люди изучают ваши привычки")
    print("2. 7 признаков что вами манипулируют")
    print("3. Психология лжи: как распознать обман")
    print("4. 5 способов защититься от газлайтинга")

    # Ввод данных
    print("\n" + "=" * 80)
    topic = input("📝 Введите тему видео: ").strip()

    if not topic:
        topic = "Как токсичные люди изучают ваши привычки"
        print(f"   Используется тема по умолчанию: {topic}")

    niche = input("🎯 Введите нишу (по умолчанию: психология): ").strip() or "психология"
    style = input("🎨 Стиль изображений (по умолчанию: minimalist_stick_figure): ").strip() or "minimalist_stick_figure"
    voice = input("🎙️ Голос (по умолчанию: rachel): ").strip() or "rachel"

    print("\n" + "=" * 80)
    print("🚀 ЗАПУСКАЮ ГЕНЕРАЦИЮ...")
    print("=" * 80)
    
    # Создаём видео
    try:
        output_path = await system.create_full_video(
            topic=topic,
            niche=niche,
            style=style,
            voice=voice,
            subtitle_style="highlighted_words"
        )
        
        print("\n" + "=" * 80)
        print("🎉 УСПЕХ!")
        print("=" * 80)
        print(f"📁 Видео сохранено: {output_path}")
        print("\n💡 Проверьте папку на рабочем столе: ~/Desktop/YouTube_Videos/")
        print("=" * 80)
        
    except Exception as e:
        print("\n" + "=" * 80)
        print("❌ ОШИБКА!")
        print("=" * 80)
        print(f"🔴 {str(e)}")
        print("\n💡 Проверьте:")
        print("   - Все API ключи добавлены в .env")
        print("   - Установлены все зависимости: pip install -r requirements.txt")
        print("   - Достаточно места на диске")
        print("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())
