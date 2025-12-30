"""
Telegram Notifier - отправка уведомлений о статусе генерации видео
"""

import os
import requests
from typing import Dict, Optional
from datetime import datetime


class TelegramNotifier:
    """Отправка уведомлений в Telegram"""
    
    def __init__(self, bot_token: str = None, chat_id: str = None):
        """
        Args:
            bot_token: Токен Telegram бота
            chat_id: ID чата для отправки уведомлений
        """
        self.bot_token = bot_token or os.getenv('TELEGRAM_BOT_TOKEN')
        self.chat_id = chat_id or os.getenv('TELEGRAM_CHAT_ID')
        
        if self.bot_token and self.chat_id:
            self.enabled = True
            print("✅ Telegram уведомления включены")
        else:
            self.enabled = False
            print("⚠️ Telegram уведомления отключены (нет токена/chat_id)")
    
    def send_message(self, text: str, parse_mode: str = 'HTML'):
        """
        Отправляет сообщение в Telegram
        
        Args:
            text: Текст сообщения
            parse_mode: Формат разметки (HTML/Markdown)
        """
        if not self.enabled:
            return
        
        try:
            url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
            
            data = {
                'chat_id': self.chat_id,
                'text': text,
                'parse_mode': parse_mode
            }
            
            response = requests.post(url, json=data, timeout=10)
            
            if response.status_code != 200:
                print(f"⚠️ Ошибка отправки в Telegram: {response.text}")
        
        except Exception as e:
            print(f"⚠️ Не удалось отправить уведомление: {e}")
    
    def notify_start(self, title: str, niche: str, style: str, voice: str):
        """Уведомление о начале генерации"""
        
        message = f"""
🚀 <b>НАЧИНАЮ ГЕНЕРАЦИЮ</b>

📌 <b>"{title}"</b>

🎯 Ниша: {niche}
🎨 Стиль: {style}
🎙️ Голос: {voice}

⏱️ Ожидаемое время: ~40-60 минут
"""
        
        self.send_message(message)
    
    def notify_progress(self, title: str, stage: str, progress: int):
        """Уведомление о прогрессе"""
        
        stages = {
            'generating_script': '✍️ Генерация скрипта',
            'generating_images': '🎨 Генерация изображений',
            'generating_audio': '🎙️ Озвучка',
            'applying_effects': '🎬 Применение эффектов',
            'editing_video': '🎞️ Монтаж видео'
        }
        
        stage_name = stages.get(stage, stage)
        
        message = f"""
⏳ <b>ПРОГРЕСС</b>

📌 "{title}"

{stage_name} ({progress}%)
"""
        
        self.send_message(message)
    
    def notify_success(
        self,
        title: str,
        metadata: Dict,
        output_path: str,
        generation_time: float
    ):
        """Уведомление об успешном завершении"""
        
        duration = metadata.get('duration', 0)
        minutes = int(duration // 60)
        seconds = int(duration % 60)
        
        gen_minutes = int(generation_time // 60)
        gen_seconds = int(generation_time % 60)
        
        message = f"""
🎉 <b>ВИДЕО ГОТОВО!</b>

📌 <b>"{title}"</b>

📊 <b>Статистика:</b>
├─ Длительность: {minutes}:{seconds:02d}
├─ Изображений: {metadata.get('image_count', 'N/A')}
├─ Язык: {metadata.get('language', 'Русский')}
├─ Стиль: {metadata.get('style', 'N/A')}
├─ Голос: {metadata.get('voice', 'N/A')}
└─ Субтитры: {metadata.get('subtitle_style', 'N/A')}

📁 Папка: {output_path}

⏱️ Время генерации: {gen_minutes}:{gen_seconds:02d}
"""
        
        self.send_message(message)
    
    def notify_error(self, title: str, stage: str, error_message: str):
        """Уведомление об ошибке"""
        
        stages = {
            'generating_script': 'Генерация скрипта',
            'generating_images': 'Генерация изображений',
            'generating_audio': 'Озвучка',
            'editing_video': 'Монтаж видео'
        }
        
        stage_name = stages.get(stage, stage)
        
        message = f"""
❌ <b>ОШИБКА ГЕНЕРАЦИИ</b>

📌 "{title}"

⚠️ Этап: {stage_name}
🔴 Ошибка: {error_message[:200]}

💡 <b>Возможное решение:</b>
Проверьте логи и статус API ключей
"""
        
        self.send_message(message)
    
    def notify_queue_complete(self, total: int, successful: int, failed: int):
        """Уведомление о завершении очереди"""
        
        message = f"""
🎉 <b>ОЧЕРЕДЬ ОБРАБОТАНА!</b>

📊 <b>Результаты:</b>
├─ Всего видео: {total}
├─ ✅ Успешно: {successful}
└─ ❌ Ошибок: {failed}

📁 Все видео сохранены в ~/Desktop/YouTube_Videos/
"""
        
        self.send_message(message)
