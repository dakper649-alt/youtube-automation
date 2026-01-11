"""
Whisk Inspector - разведка структуры Whisk AI
Открывает Whisk и показывает HTML структуру для определения селекторов
"""

import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# URL Whisk
WHISK_URL = "https://labs.google/fx/tools/whisk/project"

# Папка для Chrome профиля
PROFILE_DIR = os.path.join(os.path.dirname(__file__), '..', 'chrome-profile')
os.makedirs(PROFILE_DIR, exist_ok=True)

class WhiskInspector:
    def __init__(self):
        self.driver = None

    def start_browser(self):
        """Запуск Chrome с сохранением профиля"""
        print("🌐 Запуск Chrome...")

        options = Options()

        # Использовать отдельный профиль
        options.add_argument(f"--user-data-dir={PROFILE_DIR}")
        options.add_argument("--profile-directory=WhiskProfile")

        # НЕ headless - видимый браузер
        # options.add_argument("--headless")  # ОТКЛЮЧЕНО!

        # Дополнительные настройки
        options.add_argument("--start-maximized")
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
            # Ищем кнопку закрытия (крестик)
            # Возможные селекторы:
            possible_selectors = [
                "button[aria-label='Close']",
                "button[aria-label='Закрыть']",
                ".close-button",
                ".modal-close",
                "button.close",
                "[data-dismiss='modal']",
                "button:has(svg[class*='close'])",
                "button:has(span:contains('×'))"
            ]

            for selector in possible_selectors:
                try:
                    close_btn = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if close_btn.is_displayed():
                        close_btn.click()
                        print(f"✅ Закрыто приветственное окно (селектор: {selector})")
                        time.sleep(1)
                        return True
                except:
                    continue

            print("ℹ️ Приветственное окно не найдено (возможно, уже закрыто)")
            return False

        except Exception as e:
            print(f"⚠️ Ошибка закрытия приветственного окна: {e}")
            return False

    def inspect_page_structure(self):
        """Проверка структуры страницы"""
        print("\n" + "="*60)
        print("📋 СТРУКТУРА СТРАНИЦЫ WHISK")
        print("="*60 + "\n")

        # 1. Найти поле промпта
        print("🔍 1. Поиск поля промпта...")
        prompt_selectors = [
            "textarea",
            "input[type='text']",
            "[contenteditable='true']",
            "[placeholder*='prompt']",
            "[placeholder*='describe']",
            "textarea[name*='prompt']"
        ]

        for selector in prompt_selectors:
            elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
            if elements:
                for i, elem in enumerate(elements):
                    print(f"   ✅ Найдено поле: {selector}")
                    print(f"      - Видимо: {elem.is_displayed()}")
                    print(f"      - Placeholder: {elem.get_attribute('placeholder')}")
                    print(f"      - Name: {elem.get_attribute('name')}")
                    print(f"      - ID: {elem.get_attribute('id')}")
                    print(f"      - Class: {elem.get_attribute('class')}")
                    print()

        # 2. Найти кнопку Generate
        print("🔍 2. Поиск кнопки Generate...")
        button_selectors = [
            "button:has-text('Generate')",
            "button:has-text('Create')",
            "button[type='submit']",
            "button:contains('Generate')",
            ".generate-button",
            "[aria-label*='generate']"
        ]

        buttons = self.driver.find_elements(By.TAG_NAME, "button")
        for btn in buttons:
            text = btn.text.lower()
            if 'generat' in text or 'create' in text or 'submit' in text:
                print(f"   ✅ Найдена кнопка: '{btn.text}'")
                print(f"      - Class: {btn.get_attribute('class')}")
                print(f"      - ID: {btn.get_attribute('id')}")
                print(f"      - Type: {btn.get_attribute('type')}")
                print()

        # 3. Найти область результатов
        print("🔍 3. Поиск области результатов...")
        result_selectors = [
            ".result",
            ".output",
            ".generated-image",
            "[role='img']",
            "img[alt*='generated']"
        ]

        for selector in result_selectors:
            elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
            if elements:
                print(f"   ✅ Найдено {len(elements)} элементов: {selector}")

        # 4. Вывести весь HTML (первые 5000 символов)
        print("\n🔍 4. HTML страницы (первые 5000 символов):")
        print("-" * 60)
        html = self.driver.page_source[:5000]
        print(html)
        print("-" * 60)

        # 5. Сохранить полный HTML в файл
        html_file = os.path.join(os.path.dirname(__file__), 'whisk_page.html')
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(self.driver.page_source)
        print(f"\n💾 Полный HTML сохранён в: {html_file}")

        # 6. Сделать скриншот
        screenshot_file = os.path.join(os.path.dirname(__file__), 'whisk_screenshot.png')
        self.driver.save_screenshot(screenshot_file)
        print(f"📸 Скриншот сохранён в: {screenshot_file}")

    def wait_for_manual_inspection(self):
        """Ждать пока пользователь сам изучит страницу"""
        print("\n" + "="*60)
        print("👁️ РУЧНАЯ ПРОВЕРКА")
        print("="*60)
        print("\nБраузер открыт - изучите страницу Whisk:")
        print("1. Где находится поле для промпта?")
        print("2. Где кнопка Generate?")
        print("3. Где появляются результаты?")
        print("4. Есть ли боковая панель для референсов?")
        print("\nНажмите Enter когда закончите изучение...")
        input()

    def close_browser(self):
        """Закрыть браузер"""
        if self.driver:
            print("🔴 Закрытие браузера...")
            self.driver.quit()
            print("✅ Браузер закрыт")

def main():
    """Основная функция"""
    inspector = WhiskInspector()

    try:
        # Запустить браузер
        inspector.start_browser()

        # Открыть Whisk
        inspector.open_whisk()

        # Попытаться закрыть приветственное окно
        inspector.close_welcome_popup()

        # Проверить структуру
        inspector.inspect_page_structure()

        # Ждать ручной проверки
        inspector.wait_for_manual_inspection()

    except Exception as e:
        print(f"\n❌ ОШИБКА: {e}")
        import traceback
        traceback.print_exc()

    finally:
        # Закрыть браузер
        inspector.close_browser()

if __name__ == "__main__":
    print("\n" + "="*60)
    print("🔍 WHISK INSPECTOR - Разведка структуры Whisk AI")
    print("="*60 + "\n")

    main()

    print("\n✅ Разведка завершена!")
    print("📁 Проверьте файлы:")
    print("   - backend/services/whisk_page.html")
    print("   - backend/services/whisk_screenshot.png")
