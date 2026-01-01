"""
Flask API для Electron приложения
Простая версия без MainOrchestrator (пока)
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import time
import uuid
from threading import Thread
import random

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

        # Запускаем "генерацию" в отдельном потоке
        thread = Thread(target=simulate_generation, args=(task_id,))
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

def simulate_generation(task_id):
    """
    Симуляция генерации видео (для тестирования UI)
    ПОТОМ заменим на реальный MainOrchestrator
    """
    try:
        steps = [
            (5, 'Инициализация...', 60),
            (10, 'Генерация скрипта через Gemini...', 58),
            (15, 'Скрипт создан, начинаем генерацию изображений...', 55),
            (25, 'Генерация изображений: 20/80...', 45),
            (35, 'Генерация изображений: 40/80...', 35),
            (45, 'Генерация изображений: 60/80...', 25),
            (55, 'Генерация изображений: 80/80 - завершено!', 20),
            (60, 'Создание озвучки через ElevenLabs...', 18),
            (70, 'Применение Ken Burns эффектов...', 12),
            (80, 'Генерация субтитров...', 8),
            (90, 'Рендер финального видео через Remotion...', 5),
            (95, 'Создание SEO метаданных...', 2),
            (100, 'Готово!', 0),
        ]

        for progress, step, time_remaining in steps:
            tasks[task_id].update({
                'progress': progress,
                'step': step,
                'timeRemaining': time_remaining
            })

            # Задержка между шагами (имитация работы)
            time.sleep(2)  # 2 секунды между обновлениями

        # Завершение
        tasks[task_id].update({
            'status': 'completed',
            'progress': 100,
            'step': 'Видео готово!',
            'timeRemaining': 0,
            'video': {
                'title': tasks[task_id]['data']['topic'],
                'duration': '12:34',
                'path': '/Users/nikitamoskalev/Desktop/YouTube_Videos/test_video.mp4'
            }
        })

    except Exception as e:
        print(f"Error in simulate_generation: {e}")
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
    print("=" * 80)
    print()

    app.run(host='127.0.0.1', port=5000, debug=False, threaded=True)
