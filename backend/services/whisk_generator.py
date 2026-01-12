"""
Whisk Image Generator - Генерация изображений через Whisk AI
Интегрирует с YouTube Automation Studio для создания изображений из сценариев
"""

import os
import time
import requests
from typing import List, Dict, Optional
from datetime import datetime
try:
    import undetected_chromedriver as uc
except ImportError:
    print("⚠️ undetected_chromedriver не установлен. Используем обычный selenium.")
    import selenium.webdriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

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
        """Запуск Chrome с undetected_chromedriver"""
        print("🌐 Запуск Chrome для Whisk (undetected mode)...")

        options = uc.ChromeOptions()

        # Использовать отдельный профиль
        options.add_argument(f"--user-data-dir={PROFILE_DIR}")
        options.add_argument("--profile-directory=WhiskProfile")

        # НЕ headless - Whisk требует видимый браузер
        options.add_argument("--start-maximized")
        options.add_argument("--no-first-run")
        options.add_argument("--no-default-browser-check")

        try:
            self.driver = uc.Chrome(options=options, use_subprocess=True)
            print("✅ Chrome запущен (undetected)")
        except Exception as e:
            print(f"⚠️ Ошибка запуска undetected Chrome: {e}")
            print("   Пытаюсь запустить обычный Chrome...")
            from selenium import webdriver
            from selenium.webdriver.chrome.service import Service
            from webdriver_manager.chrome import ChromeDriverManager
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=options)
            print("✅ Chrome запущен (обычный режим)")

        return self.driver

    def open_whisk(self):
        """Открыть Whisk"""
        print(f"🌟 Открытие Whisk: {WHISK_URL}")
        self.driver.get(WHISK_URL)

        # Ждать загрузки страницы
        time.sleep(5)

        print("✅ Whisk открыт")

    def close_popups(self):
        """Закрыть все попапы и модальные окна"""
        print("🔍 Закрытие попапов...")

        try:
            # Список возможных селекторов для кнопок закрытия
            close_selectors = [
                "button[aria-label='Close']",
                "button[aria-label='Закрыть']",
                ".close-button",
                ".modal-close",
                "button.close",
                "[data-dismiss='modal']",
                "button[class*='close']",
                "button[class*='dismiss']"
            ]

            closed_count = 0
            for selector in close_selectors:
                try:
                    buttons = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for btn in buttons:
                        if btn.is_displayed():
                            btn.click()
                            closed_count += 1
                            time.sleep(0.5)
                except:
                    continue

            if closed_count > 0:
                print(f"✅ Закрыто попапов: {closed_count}")
                time.sleep(1)
            else:
                print("ℹ️ Попапы не найдены")

            return True

        except Exception as e:
            print(f"⚠️ Ошибка закрытия попапов: {e}")
            return False

    def close_welcome_popup(self):
        """Алиас для close_popups (обратная совместимость)"""
        return self.close_popups()

    def clear_prompt_field(self):
        """Очистить поле промпта"""
        try:
            # Ищем поле ввода промпта
            prompt_selectors = [
                "textarea[placeholder*='describe']",
                "textarea[placeholder*='Describe']",
                "textarea",
                "input[type='text']",
                "[contenteditable='true']"
            ]

            for selector in prompt_selectors:
                try:
                    field = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if field.is_displayed():
                        field.clear()
                        field.send_keys(Keys.CONTROL + "a")
                        field.send_keys(Keys.DELETE)
                        print("✅ Поле промпта очищено")
                        return True
                except:
                    continue

            print("⚠️ Поле промпта не найдено")
            return False

        except Exception as e:
            print(f"❌ Ошибка очистки поля: {e}")
            return False

    def enter_prompt(self, prompt: str):
        """Ввести промпт в поле"""
        try:
            # Ищем поле ввода
            prompt_selectors = [
                "textarea[placeholder*='describe']",
                "textarea[placeholder*='Describe']",
                "textarea",
                "input[type='text']",
                "[contenteditable='true']"
            ]

            for selector in prompt_selectors:
                try:
                    field = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if field.is_displayed():
                        field.click()
                        time.sleep(0.3)
                        field.send_keys(prompt)
                        print(f"✅ Введён промпт: {prompt[:50]}...")
                        return True
                except:
                    continue

            print("⚠️ Не удалось ввести промпт")
            return False

        except Exception as e:
            print(f"❌ Ошибка ввода промпта: {e}")
            return False

    def click_generate(self):
        """Нажать кнопку генерации"""
        try:
            # Используем селектор из спецификации пользователя
            generate_selectors = [
                "button[aria-label='Отправить запрос']",
                "button[aria-label='Submit']",
                "button[aria-label='Generate']",
                "button:contains('Generate')",
                "button.generate-button",
                "button[type='submit']"
            ]

            for selector in generate_selectors:
                try:
                    button = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if button.is_displayed() and button.is_enabled():
                        button.click()
                        print("✅ Нажата кнопка генерации")
                        return True
                except:
                    continue

            # Если не нашли по селекторам, ищем по тексту
            try:
                buttons = self.driver.find_elements(By.TAG_NAME, "button")
                for btn in buttons:
                    if btn.is_displayed() and 'generate' in btn.text.lower():
                        btn.click()
                        print(f"✅ Нажата кнопка: {btn.text}")
                        return True
            except:
                pass

            print("⚠️ Кнопка генерации не найдена")
            return False

        except Exception as e:
            print(f"❌ Ошибка нажатия кнопки: {e}")
            return False

    def wait_for_result(self, timeout: int = 60):
        """Дождаться результата генерации"""
        print(f"⏳ Ожидание результата (макс {timeout}с)...")

        try:
            # Ищем появление изображения результата
            result_selectors = [
                "img[src*='googleusercontent']",
                "img[src*='blob:']",
                "canvas",
                "img.result-image",
                "img.generated-image",
                "[class*='result'] img",
                "[class*='output'] img"
            ]

            start_time = time.time()
            while time.time() - start_time < timeout:
                for selector in result_selectors:
                    try:
                        imgs = self.driver.find_elements(By.CSS_SELECTOR, selector)
                        for img in imgs:
                            if img.is_displayed():
                                src = img.get_attribute('src')
                                if src and ('googleusercontent' in src or 'blob:' in src or len(src) > 100):
                                    print(f"✅ Результат готов!")
                                    return img
                    except:
                        continue

                time.sleep(1)
                if int(time.time() - start_time) % 10 == 0:
                    print(f"   ⏳ Прошло {int(time.time() - start_time)}с...")

            print(f"⏰ Таймаут ожидания ({timeout}с)")
            return None

        except Exception as e:
            print(f"❌ Ошибка ожидания результата: {e}")
            return None

    def save_image(self, img_element, scene_index: int) -> Optional[str]:
        """Сохранить изображение из элемента"""
        try:
            src = img_element.get_attribute('src')

            if not src:
                print("⚠️ Нет src у изображения")
                return None

            # Генерируем имя файла
            timestamp = int(time.time())
            filename = f"scene_{scene_index}_{timestamp}.png"
            filepath = os.path.join(OUTPUT_DIR, filename)

            # Скачиваем изображение
            if src.startswith('data:'):
                # Base64 изображение
                import base64
                image_data = src.split(',')[1]
                with open(filepath, 'wb') as f:
                    f.write(base64.b64decode(image_data))
            elif src.startswith('blob:'):
                # Blob изображение - скриншот элемента
                img_element.screenshot(filepath)
            else:
                # URL изображения
                response = requests.get(src, timeout=30)
                if response.status_code == 200:
                    with open(filepath, 'wb') as f:
                        f.write(response.content)
                else:
                    print(f"⚠️ Не удалось скачать изображение: HTTP {response.status_code}")
                    return None

            print(f"💾 Изображение сохранено: {filename}")
            return filepath

        except Exception as e:
            print(f"❌ Ошибка сохранения изображения: {e}")
            return None

    def generate_single_image(self, prompt: str, global_style: str = "", scene_index: int = 0) -> Optional[str]:
        """
        Генерировать одно изображение (полная реализация)

        Args:
            prompt: Промпт для изображения
            global_style: Базовый стиль
            scene_index: Индекс сцены

        Returns:
            Путь к сгенерированному изображению или None
        """
        print(f"\n📝 Генерация изображения #{scene_index + 1}...")

        # Комбинировать промпт с глобальным стилем
        full_prompt = f"{prompt}"
        if global_style:
            full_prompt += f", {global_style}"

        print(f"   Промпт: {full_prompt[:100]}...")

        try:
            # 1. Очистить поле промпта
            if not self.clear_prompt_field():
                print("⚠️ Не удалось очистить поле")
                time.sleep(1)  # Пауза перед повтором

            # 2. Ввести промпт
            if not self.enter_prompt(full_prompt):
                raise Exception("Не удалось ввести промпт")

            time.sleep(0.5)

            # 3. Нажать кнопку генерации
            if not self.click_generate():
                raise Exception("Не удалось нажать кнопку генерации")

            # 4. Дождаться результата
            img_element = self.wait_for_result(timeout=60)
            if not img_element:
                raise Exception("Не дождались результата генерации")

            # 5. Сохранить изображение
            image_path = self.save_image(img_element, scene_index)
            if not image_path:
                raise Exception("Не удалось сохранить изображение")

            print(f"✅ Изображение #{scene_index + 1} готово!")
            return image_path

        except Exception as e:
            print(f"❌ Ошибка генерации изображения: {e}")
            return None

    def generate_image(self, prompt: str, global_style: str = "", references: List[str] = None) -> Optional[str]:
        """Алиас для generate_single_image (обратная совместимость)"""
        return self.generate_single_image(prompt, global_style, 0)

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
                print(f"\n{'='*60}")
                print(f"СЦЕНА {i+1}/{len(scenes)}")
                print(f"{'='*60}")

                # Получить промпт из сцены
                # Используем image_prompt если есть, иначе text
                prompt = scene.get('image_prompt', scene.get('text', ''))

                # Получить scene_id для имени файла
                scene_id = scene.get('scene_id', i)

                # Попытки генерации с повторами
                image_path = None
                for attempt in range(self.retries):
                    if attempt > 0:
                        print(f"\n🔄 Повторная попытка {attempt+1}/{self.retries}...")
                        time.sleep(self.retry_delay)

                    image_path = self.generate_single_image(prompt, global_style, scene_id)

                    if image_path:
                        break
                    else:
                        print(f"⚠️ Попытка {attempt+1} не удалась")

                if image_path:
                    images.append({
                        'scene_index': scene_id,
                        'path': image_path,
                        'prompt': prompt
                    })
                    self.stats['successful'] += 1
                    print(f"✅ Изображение {i+1}/{len(scenes)} создано!")
                else:
                    self.stats['failed'] += 1
                    print(f"❌ Не удалось создать изображение {i+1}/{len(scenes)}")

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
