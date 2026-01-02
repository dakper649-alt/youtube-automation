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

        # Инициализируем оркестратор
        orchestrator = YouTubeAutomationOrchestrator(use_remotion=True)
        progress_callback('init', 5, 58)

        # Запускаем создание видео
        topic = data.get('topic', 'Untitled Video')
        niche = data.get('niche', 'general')
        style = data.get('style', 'minimalist_stick_figure')
        voice = data.get('voice', 'rachel')

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

if __name__ == '__main__':
    print("\n" + "=" * 80)
    print("🚀 FLASK API SERVER")
    print("=" * 80)
    print("Server: http://localhost:5001")
    print("Health: http://localhost:5001/api/health")
    print("=" * 80)
    print()

    app.run(host='127.0.0.1', port=5001, debug=False, threaded=True)
