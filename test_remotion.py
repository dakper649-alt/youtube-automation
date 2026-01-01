"""
Тест Remotion рендера
Создаёт короткое видео (5 сек) для проверки эффектов
"""

import asyncio
import sys
from pathlib import Path

# Добавляем путь к backend
sys.path.insert(0, str(Path(__file__).parent / 'backend'))

from services.remotion_renderer import RemotionRenderer


async def test_remotion():
    print("\n╔" + "=" * 78 + "╗")
    print("║" + " " * 20 + "🧪 ТЕСТ REMOTION РЕНДЕРА" + " " * 33 + "║")
    print("╚" + "=" * 78 + "╝")

    # Создаём тестовые сцены
    # ВАЖНО: Замените пути на реальные изображения на вашем компьютере
    test_scenes = [
        {
            'imagePath': 'path/to/test_image_1.jpg',  # <- Замените на реальный путь
            'duration': 2.0,
            'effect': 'zoom_in',
            'subtitle': {
                'text': 'Привет, мир!',
                'startTime': 0,
                'endTime': 2.0,
                'highlighted': True
            }
        },
        {
            'imagePath': 'path/to/test_image_2.jpg',  # <- Замените на реальный путь
            'duration': 2.0,
            'effect': 'pan_right',
            'subtitle': {
                'text': 'Это Remotion рендер',
                'startTime': 0,
                'endTime': 2.0,
                'highlighted': False
            }
        }
    ]

    print("\n⚠️  ВАЖНО: Перед запуском обновите пути к изображениям в test_remotion.py")
    print("   Замените 'path/to/test_image_X.jpg' на реальные пути")
    print()

    # Проверяем, обновлены ли пути
    if 'path/to/' in test_scenes[0]['imagePath']:
        print("❌ Пути к изображениям не обновлены!")
        print("   Откройте test_remotion.py и укажите реальные пути к изображениям")
        print()
        print("💡 Пример:")
        print("   'imagePath': '/home/user/Desktop/image1.jpg'")
        return

    try:
        # Инициализация рендерера
        renderer = RemotionRenderer()

        # Рендер
        print("\n🎬 Запускаю тестовый рендер...")
        output = renderer.render_video(
            scenes=test_scenes,
            output_path='test_remotion_output.mp4',
            fps=30,
            width=1920,
            height=1080
        )

        print(f"\n✅ ТЕСТ УСПЕШЕН!")
        print(f"📁 Видео сохранено: {output}")
        print(f"💡 Открой файл чтобы проверить качество эффектов")

    except Exception as e:
        print(f"\n❌ ОШИБКА: {e}")
        import traceback
        traceback.print_exc()
        print()
        print("💡 Возможные причины:")
        print("   - Remotion не установлен (cd remotion-renderer && npm install)")
        print("   - Node.js не установлен")
        print("   - Неверные пути к изображениям")


if __name__ == "__main__":
    asyncio.run(test_remotion())
