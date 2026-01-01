"""
Remotion Video Renderer
Профессиональные эффекты через Remotion
"""

import os
import json
import subprocess
from typing import List, Dict, Optional
from pathlib import Path

class RemotionRenderer:
    """Рендер видео через Remotion с профессиональными эффектами"""

    def __init__(self, remotion_dir: str = None):
        """
        Args:
            remotion_dir: Путь к Remotion проекту
        """
        if remotion_dir is None:
            # По умолчанию ищем в соседней папке
            project_root = Path(__file__).parent.parent.parent
            remotion_dir = project_root / 'remotion-renderer'

        self.remotion_dir = Path(remotion_dir)

        if not self.remotion_dir.exists():
            raise FileNotFoundError(f"Remotion проект не найден: {self.remotion_dir}")

        print(f"✅ RemotionRenderer инициализирован: {self.remotion_dir}")

    def render_video(
        self,
        scenes: List[Dict],
        audio_path: Optional[str] = None,
        output_path: str = 'output.mp4',
        fps: int = 30,
        width: int = 1920,
        height: int = 1080
    ) -> str:
        """
        Рендер видео с профессиональными эффектами

        Args:
            scenes: Список сцен с изображениями и эффектами
            audio_path: Путь к аудио файлу
            output_path: Путь для сохранения видео
            fps: FPS видео
            width: Ширина видео
            height: Высота видео

        Returns:
            Путь к готовому видео
        """

        print(f"\n{'=' * 80}")
        print("🎬 REMOTION RENDERER - ПРОФЕССИОНАЛЬНЫЙ РЕНДЕР")
        print(f"{'=' * 80}")
        print(f"Сцен: {len(scenes)}")
        print(f"FPS: {fps}")
        print(f"Разрешение: {width}x{height}")

        # Генерируем конфиг для Remotion
        config = {
            'scenes': scenes,
            'audioPath': audio_path,
            'fps': fps,
            'width': width,
            'height': height
        }

        config_path = self.remotion_dir / 'src' / 'config.json'
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)

        print(f"\n✅ Конфиг создан: {config_path}")

        # Рендер через Remotion CLI
        print("\n🎬 Запускаю рендер...")

        output_abs_path = Path(output_path).absolute()

        cmd = [
            'npx', 'remotion', 'render',
            'src/index.tsx',
            str(output_abs_path),
            '--codec', 'h264',
            '--concurrency', '4'
        ]

        try:
            result = subprocess.run(
                cmd,
                cwd=self.remotion_dir,
                capture_output=True,
                text=True,
                timeout=600  # 10 минут максимум
            )

            if result.returncode == 0:
                print(f"\n✅ Видео готово: {output_abs_path}")
                return str(output_abs_path)
            else:
                print(f"\n❌ ОШИБКА РЕНДЕРА:")
                print(result.stderr)
                raise RuntimeError(f"Remotion render failed: {result.stderr}")

        except subprocess.TimeoutExpired:
            raise RuntimeError("Рендер превысил таймаут (10 минут)")
        except FileNotFoundError:
            raise RuntimeError(
                "Remotion не найден! Установите: npm install -g @remotion/cli"
            )
