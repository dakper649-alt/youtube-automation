"""
Flask API для Electron приложения
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import sys
import os
import asyncio
from threading import Thread
import uuid
import subprocess

# Добавляем backend в путь
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from main_orchestrator import YouTubeAutomationOrchestrator

app = Flask(__name__)
CORS(app)

# Хранилище активных задач
tasks = {}


@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({'status': 'ok', 'message': 'Flask server is running'})


@app.route('/api/create-video', methods=['POST'])
def create_video():
    """Создать новое видео"""
    data = request.json

    task_id = str(uuid.uuid4())

    # Запускаем генерацию в отдельном потоке
    thread = Thread(target=run_generation, args=(task_id, data))
    thread.daemon = True
    thread.start()

    tasks[task_id] = {
        'status': 'running',
        'progress': 0,
        'step': 'Инициализация...',
        'timeRemaining': 60
    }

    return jsonify({
        'success': True,
        'task_id': task_id
    })


@app.route('/api/progress/<task_id>', methods=['GET'])
def get_progress(task_id):
    """Получить прогресс генерации"""
    if task_id not in tasks:
        return jsonify({'error': 'Task not found'}), 404

    return jsonify(tasks[task_id])


@app.route('/api/open-file', methods=['POST'])
def open_file():
    """Открыть файл в системном приложении"""
    data = request.json
    file_path = data.get('path')

    if not file_path or not os.path.exists(file_path):
        return jsonify({'error': 'File not found'}), 404

    try:
        # Open file with default application
        if sys.platform == 'darwin':  # macOS
            subprocess.run(['open', file_path])
        elif sys.platform == 'win32':  # Windows
            os.startfile(file_path)
        else:  # Linux
            subprocess.run(['xdg-open', file_path])

        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


def run_generation(task_id, data):
    """Запуск генерации видео"""
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        # Progress callback
        def on_progress(step):
            # Map step names to progress percentages
            progress_map = {
                'generating_script': 20,
                'generating_images': 40,
                'applying_effects': 60,
                'generating_audio': 75,
                'editing_video': 90
            }

            progress = progress_map.get(step, 10)
            time_remaining = int((100 - progress) / 100 * 60)

            step_names = {
                'generating_script': '📝 Генерация скрипта...',
                'generating_images': '🎨 Генерация изображений...',
                'applying_effects': '🎬 Применение эффектов...',
                'generating_audio': '🎙️ Генерация озвучки...',
                'editing_video': '🎞️ Монтаж видео...'
            }

            tasks[task_id].update({
                'step': step_names.get(step, step),
                'progress': progress,
                'timeRemaining': time_remaining
            })

        # Создаём оркестратор
        use_remotion = data.get('use_remotion', True)
        orchestrator = YouTubeAutomationOrchestrator(use_remotion=use_remotion)

        # Генерация видео
        result_path = loop.run_until_complete(
            orchestrator.create_full_video(
                topic=data['topic'],
                niche=data.get('niche', 'psychology'),
                style=data.get('style', 'minimalist_stick_figure'),
                voice=data.get('voice', 'rachel'),
                subtitle_style=data.get('subtitle_style', 'highlighted_words'),
                on_progress=on_progress
            )
        )

        tasks[task_id].update({
            'status': 'completed',
            'progress': 100,
            'step': '✅ Готово!',
            'video': {
                'title': data['topic'],
                'path': result_path,
                'duration': '10:00'
            }
        })

    except Exception as e:
        print(f"❌ Error in generation: {e}")
        import traceback
        traceback.print_exc()

        tasks[task_id].update({
            'status': 'error',
            'error': str(e)
        })


if __name__ == '__main__':
    print("\n" + "=" * 80)
    print("🚀 FLASK API SERVER")
    print("=" * 80)
    print("Server: http://localhost:5000")
    print("Health: http://localhost:5000/api/health")
    print("=" * 80 + "\n")

    app.run(host='127.0.0.1', port=5000, debug=False, threaded=True)
