# YouTube Automation Studio - Desktop App

Профессиональное Desktop приложение для автоматической генерации YouTube видео с AI.

## Особенности

- ✅ Красивый UI с градиентами
- ✅ Прогресс в реальном времени
- ✅ Интеграция с Flask API backend
- ✅ Поддержка Remotion и MoviePy рендереров
- ✅ Управление готовыми видео
- ✅ Настройки API ключей

## Установка

### 1. Установить Node.js зависимости

```bash
cd youtube-automation-app
npm install
```

### 2. Установить Python зависимости (если ещё не установлены)

```bash
cd ..
pip install flask flask-cors
```

## Запуск

### Способ 1: Через Electron (рекомендуется)

```bash
cd youtube-automation-app
npm start
```

Electron автоматически запустит Flask backend.

### Способ 2: Раздельный запуск

**Терминал 1 - Flask backend:**
```bash
python api/server.py
```

**Терминал 2 - Electron app:**
```bash
cd youtube-automation-app
npm start
```

## Сборка приложения

### macOS

```bash
npm run build-mac
```

Создаст `.dmg` и `.zip` файлы в папке `dist/`.

## Структура

```
youtube-automation-app/
├── main.js              # Electron main process
├── preload.js           # Preload скрипт для безопасности
├── package.json         # NPM конфигурация
└── renderer/
    ├── index.html       # Главная страница
    ├── styles.css       # Стили
    └── app.js           # UI логика
```

## API Endpoints

Flask сервер (`api/server.py`) предоставляет:

- `GET /api/health` - Health check
- `POST /api/create-video` - Создать видео (использует MainOrchestrator для РЕАЛЬНОЙ генерации)
- `GET /api/progress/<task_id>` - Получить прогресс в реальном времени
- `GET /api/videos` - Получить список готовых видео
- `POST /api/open-file` - Открыть файл в системном приложении

## Использование

1. Запустите приложение
2. Введите тему видео
3. Выберите настройки (ниша, стиль, голос, длина)
4. Нажмите "Создать видео"
5. Следите за прогрессом
6. Открывайте готовые видео

## Troubleshooting

**"Flask server not ready"**
- Убедитесь что Python venv активирован
- Проверьте что Flask установлен: `pip list | grep -i flask`

**"Connection refused"**
- Flask сервер должен быть запущен на порту 5001
- Проверьте: `curl http://localhost:5001/api/health`

**Видео не создаётся**
- Проверьте API ключи в `.env`
- Убедитесь что все зависимости установлены
- Проверьте логи в консоли

## Разработка

Для режима разработки с DevTools:

```bash
NODE_ENV=development npm start
```
