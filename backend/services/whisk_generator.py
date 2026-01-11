"""
Whisk Image Generator - Генерация изображений через Whisk AI
Интегрирует с YouTube Automation Studio для создания изображений из сценариев
"""

import os
import time
from typing import List, Dict, Optional
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# Whisk URL
WHISK_URL = "https://labs.google/fx/tools/whisk/project"

# Chrome profile directory
PROFILE_DIR = os.path.join(os.path.dirname(__file__), '..', 'chrome-profile')
os.makedirs(PROFILE_DIR, exist_ok=True)

# Output directory for generated images
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), '..', 'generated_images')
os.makedirs(OUTPUT_DIR, exist_ok=True)


class WhiskGenerator:
    """
    Генератор изображений через Whisk AI
    """

    def __init__(self, retries: int = 2, retry_delay: int = 5):
        """
        Инициализация генератора

        Args:
            retries: Количество попыток перед fallback
            retry_delay: Задержка между попытками (секунды)
        """
        self.driver = None
        self.retries = retries
        self.retry_delay = retry_delay
        self.stats = {
            'total_images': 0,
            'successful': 0,
            'failed': 0,
            'total_time': 0
        }

    def start_browser(self):
        """Запуск Chrome с персистентным профилем"""
        print("🌐 Запуск Chrome для Whisk...")

        options = Options()

        # Использовать отдельный профиль для авторизации
        options.add_argument(f"--user-data-dir={PROFILE_DIR}")
        options.add_argument("--profile-directory=WhiskProfile")

        # НЕ headless - Whisk требует видимый браузер
        options.add_argument("--start-maximized")

        # Анти-детект настройки
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)

        # Автоматическая установка ChromeDriver
        service = Service(ChromeDriverManager().install())

        self.driver = webdriver.Chrome(service=service, options=options)

        print("✅ Chrome запущен")
        return self.driver

    def open_whisk(self):
        """Открыть Whisk"""
        print(f"🌟 Открытие Whisk: {WHISK_URL}")
        self.driver.get(WHISK_URL)

        # Ждать загрузки страницы
        time.sleep(5)

        print("✅ Whisk открыт")

    def close_welcome_popup(self):
        """Попытка закрыть приветственное окно"""
        print("🔍 Поиск приветственного окна...")

        try:
            possible_selectors = [
                "button[aria-label='Close']",
                "button[aria-label='Закрыть']",
                ".close-button",
                ".modal-close",
                "button.close",
                "[data-dismiss='modal']"
            ]

            for selector in possible_selectors:
                try:
                    close_btn = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if close_btn.is_displayed():
                        close_btn.click()
                        print(f"✅ Закрыто приветственное окно")
                        time.sleep(1)
                        return True
                except:
                    continue

            print("ℹ️ Приветственное окно не найдено")
            return False

        except Exception as e:
            print(f"⚠️ Ошибка закрытия приветственного окна: {e}")
            return False

    def generate_image(self, prompt: str, global_style: str = "", references: List[str] = None) -> Optional[str]:
        """
        Генерировать одно изображение

        Args:
            prompt: Промпт для изображения
            global_style: Базовый стиль
            references: Список путей к референсам

        Returns:
            Путь к сгенерированному изображению или None
        """
        print(f"\n📝 Генерация изображения...")
        print(f"   Промпт: {prompt[:100]}...")

        # Комбинировать промпт с глобальным стилем
        full_prompt = f"{prompt}"
        if global_style:
            full_prompt += f", {global_style}"

        print(f"   Полный промпт: {full_prompt[:150]}...")

        try:
            # ЗАГЛУШКА: В реальной реализации здесь должна быть работа с Whisk
            # Найти поле промпта, ввести текст, нажать Generate, дождаться результата

            # Симуляция генерации
            time.sleep(2)

            # TODO: Реальная реализация:
            # 1. Найти поле промпта (textarea, input[type='text'], или [contenteditable='true'])
            # 2. Очистить поле
            # 3. Ввести full_prompt
            # 4. Если есть references - загрузить их
            # 5. Нажать кнопку Generate
            # 6. Дождаться появления результата (может занять 5-15 секунд)
            # 7. Скачать изображение
            # 8. Сохранить в OUTPUT_DIR

            print(f"⚠️ ЗАГЛУШКА: Генерация пока не реализована")
            print(f"   В реальной версии здесь будет взаимодействие с Whisk AI")

            return None

        except Exception as e:
            print(f"❌ Ошибка генерации: {e}")
            return None

    def generate_images_for_scenes(
        self,
        scenes: List[Dict],
        global_style: str = "",
        references: List[str] = None,
        auto_download: bool = True
    ) -> Dict:
        """
        Генерировать изображения для всех сцен

        Args:
            scenes: Список сцен [{index: 0, text: "...", sentences: [...]}, ...]
            global_style: Базовый стиль для всех изображений
            references: Список путей к референсам
            auto_download: Автоматически скачивать результаты

        Returns:
            Результат генерации с путями к изображениям и статистикой
        """
        start_time = time.time()

        print("\n" + "="*60)
        print("🎬 ГЕНЕРАЦИЯ ИЗОБРАЖЕНИЙ")
        print("="*60)
        print(f"Сцен: {len(scenes)}")
        print(f"Глобальный стиль: {global_style if global_style else 'не задан'}")
        print(f"Референсов: {len(references) if references else 0}")
        print("="*60 + "\n")

        images = []
        self.stats['total_images'] = len(scenes)

        try:
            # Запустить браузер
            self.start_browser()

            # Открыть Whisk
            self.open_whisk()

            # Закрыть приветственное окно
            self.close_welcome_popup()

            # Генерировать изображения для каждой сцены
            for i, scene in enumerate(scenes):
                print(f"\n--- Сцена {i+1}/{len(scenes)} ---")

                # Использовать текст сцены как промпт
                prompt = scene['text']

                # Попытки генерации с повторами
                image_path = None
                for attempt in range(self.retries):
                    if attempt > 0:
                        print(f"🔄 Повторная попытка {attempt+1}/{self.retries}...")
                        time.sleep(self.retry_delay)

                    image_path = self.generate_image(prompt, global_style, references)

                    if image_path:
                        break

                if image_path:
                    images.append({
                        'scene_index': scene['index'],
                        'path': image_path,
                        'prompt': prompt
                    })
                    self.stats['successful'] += 1
                    print(f"✅ Изображение {i+1} создано")
                else:
                    self.stats['failed'] += 1
                    print(f"❌ Не удалось создать изображение {i+1}")

        except Exception as e:
            print(f"\n❌ КРИТИЧЕСКАЯ ОШИБКА: {e}")
            import traceback
            traceback.print_exc()

        finally:
            # Закрыть браузер
            self.close_browser()

        # Подсчитать статистику
        end_time = time.time()
        self.stats['total_time'] = round(end_time - start_time, 2)

        print("\n" + "="*60)
        print("📊 ИТОГИ ГЕНЕРАЦИИ")
        print("="*60)
        print(f"Успешно: {self.stats['successful']}/{self.stats['total_images']}")
        print(f"Ошибок: {self.stats['failed']}")
        print(f"Время: {self.stats['total_time']}с")
        print(f"Среднее время на изображение: {round(self.stats['total_time'] / max(len(scenes), 1), 2)}с")
        print("="*60 + "\n")

        return {
            'success': True,
            'images': images,
            'stats': self.stats,
            'output_dir': OUTPUT_DIR
        }

    def close_browser(self):
        """Закрыть браузер"""
        if self.driver:
            print("🔴 Закрытие браузера...")
            self.driver.quit()
            print("✅ Браузер закрыт")


# Функция для тестирования
def test_whisk_generator():
    """Тестовая функция"""
    generator = WhiskGenerator(retries=2, retry_delay=5)

    # Тестовые сцены
    scenes = [
        {'index': 0, 'text': 'A beautiful sunset over the ocean.', 'sentences': ['A beautiful sunset over the ocean']},
        {'index': 1, 'text': 'A majestic mountain landscape.', 'sentences': ['A majestic mountain landscape']},
    ]

    # Запустить генерацию
    result = generator.generate_images_for_scenes(
        scenes=scenes,
        global_style="digital art, vibrant colors, high quality",
        references=None,
        auto_download=True
    )

    print("\n🎉 Результат:")
    print(result)


if __name__ == "__main__":
    print("\n" + "="*60)
    print("🎬 WHISK GENERATOR - Тест генерации изображений")
    print("="*60 + "\n")

    test_whisk_generator()
