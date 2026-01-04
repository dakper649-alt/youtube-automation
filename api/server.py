"""
Flask API для Electron приложения
Полная версия с MainOrchestrator для реальной генерации видео
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import time
import uuid
from threading import Thread
import sys
import os
from pathlib import Path
import asyncio

# Добавляем путь к backend для импорта
sys.path.insert(0, str(Path(__file__).parent.parent / 'backend'))

app = Flask(__name__)
CORS(app)

# Хранилище активных задач
tasks = {}

@app.route('/api/health', methods=['GET'])
def health():
    """Health check"""
    return jsonify({'status': 'ok', 'message': 'Flask API is running'})

@app.route('/api/create-video', methods=['POST'])
def create_video():
    """Создать новое видео"""
    try:
        data = request.get_json()

        if not data:
            return jsonify({'error': 'No data provided'}), 400

        # Валидация
        if 'topic' not in data:
            return jsonify({'error': 'Topic is required'}), 400

        # Создаём ID задачи
        task_id = str(uuid.uuid4())

        # Инициализируем задачу
        tasks[task_id] = {
            'status': 'running',
            'progress': 0,
            'step': 'Инициализация...',
            'timeRemaining': 60,
            'data': data
        }

        # Запускаем РЕАЛЬНУЮ генерацию в отдельном потоке
        thread = Thread(target=real_generation, args=(task_id, data))
        thread.daemon = True
        thread.start()

        return jsonify({
            'success': True,
            'task_id': task_id,
            'message': 'Video generation started'
        })

    except Exception as e:
        print(f"Error in create_video: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/progress/<task_id>', methods=['GET'])
def get_progress(task_id):
    """Получить прогресс генерации"""
    if task_id not in tasks:
        return jsonify({'error': 'Task not found'}), 404

    return jsonify(tasks[task_id])

@app.route('/api/videos', methods=['GET'])
def get_videos():
    """Получить список готовых видео"""
    # Пока возвращаем пустой список
    return jsonify({'videos': []})

def real_generation(task_id, data):
    """
    РЕАЛЬНАЯ генерация видео через MainOrchestrator
    """
    try:
        from main_orchestrator import YouTubeAutomationOrchestrator

        # Progress callback для обновления прогресса
        def progress_callback(step, progress, time_estimate=None):
            """Обновляет прогресс в реальном времени"""
            step_messages = {
                'init': 'Инициализация системы...',
                'generating_script': 'Генерация скрипта через Gemini...',
                'script_complete': 'Скрипт создан, начинаем генерацию изображений...',
                'generating_images': 'Генерация изображений через AI...',
                'images_progress_20': 'Генерация изображений: 20%...',
                'images_progress_40': 'Генерация изображений: 40%...',
                'images_progress_60': 'Генерация изображений: 60%...',
                'images_progress_80': 'Генерация изображений: 80%...',
                'images_complete': 'Все изображения сгенерированы!',
                'applying_effects': 'Применение Ken Burns эффектов...',
                'generating_audio': 'Создание озвучки через ElevenLabs...',
                'audio_complete': 'Озвучка готова!',
                'generating_subtitles': 'Генерация субтитров...',
                'editing_video': 'Рендер финального видео через Remotion...',
                'finalizing': 'Создание SEO метаданных...',
                'complete': 'Видео готово!'
            }

            message = step_messages.get(step, f'{step}...')

            tasks[task_id].update({
                'progress': progress,
                'step': message,
                'timeRemaining': time_estimate if time_estimate else max(1, int((100 - progress) * 0.6))
            })

        # Инициализация
        progress_callback('init', 0, 60)

        # Создаём event loop для async функций
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        # Инициализируем оркестратор (Remotion используется по умолчанию)
        orchestrator = YouTubeAutomationOrchestrator()
        progress_callback('init', 5, 58)

        # Запускаем создание видео
        topic = data.get('topic', 'Untitled Video')
        niche = data.get('niche', 'general')
        style = data.get('style', 'minimalist_stick_figure')
        voice = data.get('voice', 'rachel')
        music = data.get('music', 'no_music')
        use_ollama = data.get('use_ollama', True)  # По умолчанию используем Ollama

        # Создаём прогресс callback который интегрируется с MainOrchestrator
        def orchestrator_progress(step):
            """Callback для MainOrchestrator"""
            # Маппинг этапов MainOrchestrator на проценты
            progress_map = {
                'generating_script': 10,
                'script_complete': 15,
                'generating_images': 30,
                'images_complete': 55,
                'applying_effects': 65,
                'generating_audio': 75,
                'audio_complete': 80,
                'editing_video': 90,
                'finalizing': 95
            }

            progress = progress_map.get(step, 0)
            progress_callback(step, progress)

        # Запускаем полный пайплайн
        video_path = loop.run_until_complete(
            orchestrator.create_full_video(
                topic=topic,
                niche=niche,
                style=style,
                voice=voice,
                background_music=music,
                use_ollama=use_ollama,  # Передаём параметр Ollama
                on_progress=orchestrator_progress
            )
        )

        # Получаем метаданные видео (через ffprobe вместо MoviePy)
        import subprocess
        import json
        try:
            result = subprocess.run([
                'ffprobe', '-v', 'quiet', '-print_format', 'json',
                '-show_format', video_path
            ], capture_output=True, text=True)
            probe_data = json.loads(result.stdout)
            duration_seconds = int(float(probe_data['format']['duration']))
            duration_str = f"{duration_seconds // 60}:{duration_seconds % 60:02d}"
        except Exception as e:
            print(f"   ⚠️  Не удалось получить метаданные видео: {e}")
            duration_str = "N/A"

        # Завершение
        progress_callback('complete', 100, 0)

        tasks[task_id].update({
            'status': 'completed',
            'progress': 100,
            'step': 'Видео готово!',
            'timeRemaining': 0,
            'video': {
                'title': topic,
                'duration': duration_str,
                'path': video_path
            }
        })

        loop.close()

    except Exception as e:
        print(f"Error in real_generation: {e}")
        import traceback
        traceback.print_exc()

        tasks[task_id].update({
            'status': 'error',
            'error': str(e)
        })

@app.route('/api/open-file', methods=['POST'])
def open_file():
    """Открыть файл в системном приложении по умолчанию"""
    try:
        data = request.get_json()
        file_path = data.get('path')

        if not file_path:
            return jsonify({'error': 'Path is required'}), 400

        # Открываем файл в зависимости от ОС
        import platform
        import subprocess

        system = platform.system()

        if system == 'Darwin':  # macOS
            subprocess.run(['open', file_path])
        elif system == 'Windows':
            os.startfile(file_path)
        elif system == 'Linux':
            subprocess.run(['xdg-open', file_path])

        return jsonify({'success': True, 'message': f'Opened {file_path}'})

    except Exception as e:
        print(f"Error in open_file: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/preview-voice/<voice_key>', methods=['GET'])
def preview_voice(voice_key):
    """
    Генерация короткого аудио для прослушки голоса

    Args:
        voice_key: Ключ голоса (rachel, adam, bella и т.д.)

    Returns:
        MP3 файл с тестовой озвучкой
    """
    try:
        # Импортируем конфигурацию голосов
        sys.path.insert(0, str(Path(__file__).parent.parent / 'backend'))
        from config.voices import get_voice_id, get_preview_text, ELEVENLABS_VOICES

        # Проверяем, существует ли голос
        if voice_key not in ELEVENLABS_VOICES:
            return jsonify({'error': f'Голос "{voice_key}" не найден'}), 404

        voice_id = get_voice_id(voice_key)
        preview_text = get_preview_text(voice_key)

        print(f"🎤 Preview voice: {voice_key} ({ELEVENLABS_VOICES[voice_key]['name']})")

        # Генерируем короткое аудио через ElevenLabs
        import requests

        # Получаем API ключ (54 ключа!)
        from services.api_key_manager import SafeAPIManager

        # Используем безопасный менеджер с ротацией
        api_manager = SafeAPIManager()

        # Создаём event loop для async функции
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        elevenlabs_key = loop.run_until_complete(api_manager.get_safe_elevenlabs_key())
        loop.close()

        if not elevenlabs_key:
            return jsonify({'error': 'ElevenLabs API ключ не найден'}), 500

        # Генерируем аудио
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
        headers = {
            "xi-api-key": elevenlabs_key,
            "Content-Type": "application/json"
        }
        data = {
            "text": preview_text,
            "model_id": "eleven_multilingual_v2",
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.75
            }
        }

        response = requests.post(url, headers=headers, json=data, timeout=30)

        if response.status_code == 200:
            # Сохраняем временный файл
            preview_dir = Path(__file__).parent.parent / 'temp'
            preview_dir.mkdir(exist_ok=True)
            preview_path = preview_dir / f'preview_{voice_key}.mp3'

            with open(preview_path, 'wb') as f:
                f.write(response.content)

            print(f"✅ Preview generated: {preview_path}")

            # Возвращаем аудио файл
            from flask import send_file
            return send_file(str(preview_path), mimetype='audio/mpeg')
        else:
            error_msg = f'ElevenLabs API error: {response.status_code}'
            if response.text:
                error_msg += f' - {response.text[:200]}'
            print(f"❌ {error_msg}")
            return jsonify({'error': error_msg}), 500

    except Exception as e:
        print(f"❌ Error in preview_voice: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

# ═══════════════════════════════════════════════════════════════
# SETTINGS ENDPOINTS
# ═══════════════════════════════════════════════════════════════

SETTINGS_FILE = Path(__file__).parent.parent / 'settings.json'

@app.route('/api/settings', methods=['GET'])
def get_settings():
    """Получить текущие настройки"""
    try:
        if SETTINGS_FILE.exists():
            import json
            with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
                settings = json.load(f)
            return jsonify(settings)
        else:
            # Возвращаем настройки по умолчанию
            default_settings = {
                'outputFolder': '~/Desktop/YouTube_Videos',
                'autoCleanup': True,
                'language': 'ru',
                'defaultStyle': 'minimalist_stick_figure',
                'defaultVoice': 'rachel',
                'defaultMusic': 'calm_piano',
                'musicEnabled': True,
                'defaultLength': '1200',
                'telegramToken': '',
                'telegramChatId': '',
                'notifyStart': True,
                'notifyProgress': True,
                'notifyComplete': True,
                'notifyError': True,
                'theme': 'dark',
                'fontSize': 'medium',
                'animationsEnabled': True
            }
            return jsonify(default_settings)
    except Exception as e:
        print(f"Error loading settings: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/settings/save', methods=['POST'])
def save_settings():
    """Сохранить настройки в файл"""
    try:
        data = request.get_json()

        if not data:
            return jsonify({'error': 'No data provided'}), 400

        # Сохраняем настройки
        import json
        with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        print(f"✅ Settings saved to {SETTINGS_FILE}")

        return jsonify({'success': True, 'message': 'Settings saved successfully'})

    except Exception as e:
        print(f"Error saving settings: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/settings/reset', methods=['POST'])
def reset_settings():
    """Сбросить настройки к значениям по умолчанию"""
    try:
        if SETTINGS_FILE.exists():
            SETTINGS_FILE.unlink()

        print(f"✅ Settings reset to defaults")

        return jsonify({'success': True, 'message': 'Settings reset successfully'})

    except Exception as e:
        print(f"Error resetting settings: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/settings/keys', methods=['GET'])
def get_api_keys():
    """Получить список API ключей с их статусом"""
    try:
        from dotenv import load_dotenv
        import os

        # Загружаем .env файл
        env_path = Path(__file__).parent.parent / '.env'
        load_dotenv(env_path)

        # Считываем HF ключи (123 ключа)
        hf_keys = []
        for i in range(1, 124):
            key = os.getenv(f'HUGGINGFACE_TOKEN_{i}')
            if key:
                hf_keys.append({'value': key, 'active': True})

        # Считываем ElevenLabs ключи (54 ключа)
        elevenlabs_keys = []
        for i in range(1, 55):
            key = os.getenv(f'ELEVENLABS_API_KEY_{i}')
            if key:
                elevenlabs_keys.append({'value': key, 'active': True})

        # YouTube API ключи
        youtube_keys = []
        youtube_key = os.getenv('YOUTUBE_API_KEY')
        if youtube_key:
            youtube_keys.append({'value': youtube_key, 'active': True})

        # Groq ключи
        groq_keys = []
        groq_key = os.getenv('GROQ_API_KEY')
        if groq_key:
            groq_keys.append({'value': groq_key, 'active': True})

        response_data = {
            'huggingface': {
                'keys': hf_keys,
                'active': len(hf_keys),
                'requests': 0  # TODO: Track usage
            },
            'elevenlabs': {
                'keys': elevenlabs_keys,
                'active': len(elevenlabs_keys),
                'requests': 0  # TODO: Track usage
            },
            'youtube': {
                'keys': youtube_keys,
                'active': len(youtube_keys),
                'requests': 0  # TODO: Track usage
            },
            'groq': {
                'keys': groq_keys,
                'active': len(groq_keys),
                'requests': 0  # TODO: Track usage
            }
        }

        return jsonify(response_data)

    except Exception as e:
        print(f"Error loading API keys: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/settings/keys/add', methods=['POST'])
def add_api_key():
    """Добавить новый API ключ"""
    try:
        data = request.get_json()
        service = data.get('service')
        key = data.get('key')

        if not service or not key:
            return jsonify({'error': 'Service and key are required'}), 400

        # TODO: Implement adding key to .env file
        # For now, just return success

        return jsonify({
            'success': True,
            'message': f'Key added for {service} (requires manual .env update)'
        })

    except Exception as e:
        print(f"Error adding API key: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/settings/keys/test', methods=['POST'])
def test_api_key():
    """Протестировать API ключ"""
    try:
        data = request.get_json()
        service = data.get('service')
        index = data.get('index')

        if service is None or index is None:
            return jsonify({'error': 'Service and index are required'}), 400

        # TODO: Implement actual API key testing for each service
        # For now, just return success

        return jsonify({
            'valid': True,
            'message': f'Key {index} for {service} is valid (test not implemented yet)'
        })

    except Exception as e:
        print(f"Error testing API key: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/settings/keys/delete', methods=['POST'])
def delete_api_key():
    """Удалить API ключ"""
    try:
        data = request.get_json()
        service = data.get('service')
        index = data.get('index')

        if service is None or index is None:
            return jsonify({'error': 'Service and index are required'}), 400

        # TODO: Implement removing key from .env file
        # For now, just return success

        return jsonify({
            'success': True,
            'message': f'Key {index} removed from {service} (requires manual .env update)'
        })

    except Exception as e:
        print(f"Error deleting API key: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/test-telegram', methods=['POST'])
def test_telegram():
    """Отправить тестовое сообщение в Telegram"""
    try:
        data = request.get_json()
        token = data.get('token')
        chat_id = data.get('chatId')

        if not token or not chat_id:
            return jsonify({'error': 'Token and chatId are required'}), 400

        # Отправляем тестовое сообщение
        import requests

        url = f'https://api.telegram.org/bot{token}/sendMessage'
        payload = {
            'chat_id': chat_id,
            'text': '🎬 YouTube Automation Studio\n\n✅ Telegram интеграция работает!\n\nВы будете получать уведомления о генерации видео.',
            'parse_mode': 'HTML'
        }

        response = requests.post(url, json=payload, timeout=10)

        if response.status_code == 200:
            return jsonify({'success': True, 'message': 'Test message sent successfully'})
        else:
            error_data = response.json()
            error_msg = error_data.get('description', 'Unknown error')
            return jsonify({'error': f'Telegram API error: {error_msg}'}), 400

    except Exception as e:
        print(f"Error testing Telegram: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/choose-folder', methods=['POST'])
def choose_folder():
    """Открыть диалог выбора папки"""
    try:
        # TODO: Implement folder selection dialog
        # This would require integration with Electron's dialog API
        # For now, just return a placeholder

        return jsonify({
            'success': False,
            'message': 'Folder selection requires Electron integration'
        })

    except Exception as e:
        print(f"Error choosing folder: {e}")
        return jsonify({'error': str(e)}), 500

# ═══════════════════════════════════════════════════════════════
# STATS ENDPOINTS
# ═══════════════════════════════════════════════════════════════

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Получить статистику генерации видео"""
    try:
        # Импортируем stats_tracker
        sys.path.insert(0, str(Path(__file__).parent.parent / 'backend'))
        from services.stats_tracker import StatsTracker

        tracker = StatsTracker()
        stats = tracker.get_stats()

        return jsonify(stats)

    except Exception as e:
        print(f"Error loading stats: {e}")
        import traceback
        traceback.print_exc()

        # Возвращаем демо данные если tracker не работает
        demo_stats = {
            'overview': {
                'totalVideos': 0,
                'totalTimeMinutes': 0,
                'successRate': 0,
                'avgDurationSeconds': 0
            },
            'videosByDay': [],
            'styleUsage': {},
            'voiceUsage': {},
            'timeOfDay': {
                'morning': 0,
                'afternoon': 0,
                'evening': 0,
                'night': 0
            },
            'apiUsage': {
                'huggingface': {'used': 0, 'limit': None},
                'elevenlabs': {'used': 0, 'limit': 10000},
                'youtube': {'used': 0, 'limit': 10000},
                'groq': {'used': 0, 'limit': 14400}
            },
            'achievements': {
                'first_video': False,
                'ten_videos': False,
                'hundred_videos': False,
                'three_per_day': False,
                'ten_per_week': False,
                'thirty_day_streak': False
            },
            'goals': {
                'weekly': {'current': 0, 'target': 10},
                'monthly': {'current': 0, 'target': 40}
            }
        }

        return jsonify(demo_stats)

@app.route('/api/stats/export/csv', methods=['GET'])
def export_stats_csv():
    """Экспорт статистики в CSV"""
    try:
        import csv
        import io
        from flask import Response

        # Импортируем stats_tracker
        sys.path.insert(0, str(Path(__file__).parent.parent / 'backend'))
        from services.stats_tracker import StatsTracker

        tracker = StatsTracker()

        # Подключаемся к базе данных
        import sqlite3
        conn = sqlite3.connect(tracker.db_path)
        cursor = conn.cursor()

        # Получаем все видео
        cursor.execute('''
            SELECT topic, style, voice, music, duration_seconds,
                   generation_time_minutes, success, created_at
            FROM videos
            ORDER BY created_at DESC
        ''')
        rows = cursor.fetchall()
        conn.close()

        # Создаём CSV
        output = io.StringIO()
        writer = csv.writer(output)

        # Заголовки
        writer.writerow([
            'Тема', 'Стиль', 'Голос', 'Музыка', 'Длительность (сек)',
            'Время генерации (мин)', 'Успех', 'Создано'
        ])

        # Данные
        writer.writerows(rows)

        # Возвращаем файл
        return Response(
            output.getvalue(),
            mimetype='text/csv',
            headers={'Content-Disposition': 'attachment;filename=youtube_automation_stats.csv'}
        )

    except Exception as e:
        print(f"Error exporting CSV: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/stats/export/json', methods=['GET'])
def export_stats_json():
    """Экспорт статистики в JSON"""
    try:
        # Импортируем stats_tracker
        sys.path.insert(0, str(Path(__file__).parent.parent / 'backend'))
        from services.stats_tracker import StatsTracker

        tracker = StatsTracker()
        stats = tracker.get_stats()

        # Возвращаем JSON файл
        from flask import Response
        import json

        return Response(
            json.dumps(stats, indent=2, ensure_ascii=False),
            mimetype='application/json',
            headers={'Content-Disposition': 'attachment;filename=youtube_automation_stats.json'}
        )

    except Exception as e:
        print(f"Error exporting JSON: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

# ═══════════════════════════════════════════════════════════════
# VIDEO LIBRARY ENDPOINTS
# ═══════════════════════════════════════════════════════════════

@app.route('/api/videos', methods=['GET'])
def get_videos():
    """Получить список всех видео"""
    try:
        import sqlite3

        # Импортируем stats_tracker
        sys.path.insert(0, str(Path(__file__).parent.parent / 'backend'))
        from services.stats_tracker import StatsTracker

        tracker = StatsTracker()
        conn = sqlite3.connect(tracker.db_path)
        cursor = conn.cursor()

        # Получаем все видео
        cursor.execute('''
            SELECT id, topic, niche, style, voice, music,
                   duration_seconds, generation_time_minutes,
                   success, created_at, video_path
            FROM videos
            ORDER BY created_at DESC
        ''')

        videos = []
        for row in cursor.fetchall():
            # Определяем статус на основе поля success
            if row[8] == 1 or row[8] == '1' or row[8] == True:
                status = 'completed'
            elif row[8] == 0 or row[8] == '0' or row[8] == False:
                status = 'error'
            else:
                status = 'processing'

            videos.append({
                'id': row[0],
                'topic': row[1],
                'niche': row[2],
                'style': row[3],
                'voice': row[4],
                'music': row[5],
                'duration_seconds': row[6] or 0,
                'generation_time_minutes': row[7] or 0,
                'status': status,
                'created_at': row[9],
                'video_path': row[10],
                'thumbnail': None  # TODO: генерация превью
            })

        conn.close()

        print(f"📊 Retrieved {len(videos)} videos")
        return jsonify(videos)

    except Exception as e:
        print(f"Error loading videos: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/videos/<int:video_id>', methods=['DELETE'])
def delete_video(video_id):
    """Удалить видео"""
    try:
        import sqlite3

        # Импортируем stats_tracker
        sys.path.insert(0, str(Path(__file__).parent.parent / 'backend'))
        from services.stats_tracker import StatsTracker

        tracker = StatsTracker()
        conn = sqlite3.connect(tracker.db_path)
        cursor = conn.cursor()

        # Получить путь к видео
        cursor.execute('SELECT video_path FROM videos WHERE id = ?', (video_id,))
        result = cursor.fetchone()

        if result and result[0]:
            video_path = result[0]

            # Удалить файл если существует
            if os.path.exists(video_path):
                try:
                    os.remove(video_path)
                    print(f"🗑️ Deleted file: {video_path}")
                except Exception as e:
                    print(f"⚠️ Could not delete file {video_path}: {e}")

            # Удалить из БД
            cursor.execute('DELETE FROM videos WHERE id = ?', (video_id,))
            conn.commit()
            print(f"✅ Deleted video from database: {video_id}")

        conn.close()
        return jsonify({'success': True, 'message': f'Video {video_id} deleted'})

    except Exception as e:
        print(f"Error deleting video: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("\n" + "=" * 80)
    print("🚀 FLASK API SERVER")
    print("=" * 80)
    print("Server: http://localhost:5001")
    print("Health: http://localhost:5001/api/health")
    print("=" * 80)
    print()

    app.run(host='127.0.0.1', port=5001, debug=False, threaded=True)
