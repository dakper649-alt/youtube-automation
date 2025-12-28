"""
Главная точка входа для YouTube Automation Backend

Этот файл запускает FastAPI сервер и регистрирует все API endpoints.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

# Загрузка переменных окружения
load_dotenv()

# Создание FastAPI приложения
app = FastAPI(
    title="YouTube Automation API",
    description="API для автоматизации создания YouTube видео",
    version="1.0.0"
)

# Настройка CORS для работы с Frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Корневой endpoint"""
    return {
        "message": "YouTube Automation API",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/api/health")
async def health_check():
    """Проверка состояния сервера"""
    return {
        "status": "healthy",
        "services": {
            "youtube_api": os.getenv("YOUTUBE_API_KEY") is not None,
            "anthropic_api": os.getenv("ANTHROPIC_API_KEY") is not None,
            "openai_api": os.getenv("OPENAI_API_KEY") is not None,
            "stability_api": os.getenv("STABILITY_API_KEY") is not None,
            "elevenlabs_api": os.getenv("ELEVENLABS_API_KEY") is not None,
        }
    }


# TODO: Добавить endpoints для:
# - POST /api/analyze - Анализ YouTube канала
# - POST /api/generate/script - Генерация скрипта
# - POST /api/generate/images - Генерация изображений
# - POST /api/generate/audio - Генерация озвучки
# - POST /api/generate/subtitles - Генерация субтитров
# - POST /api/generate/video - Сборка финального видео
# - GET /api/projects - Список всех проектов
# - GET /api/projects/{id} - Детали проекта
# - DELETE /api/projects/{id} - Удаление проекта


if __name__ == "__main__":
    import uvicorn

    # Получение настроек из переменных окружения
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    debug = os.getenv("DEBUG", "True").lower() == "true"

    # Запуск сервера
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=debug
    )
