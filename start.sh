#!/bin/bash

echo "🚀 YouTube Automation Studio - Starting..."
echo "═══════════════════════════════════════════════════════════"

# Цвета для вывода
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 1. Проверка и запуск Ollama (опционально)
if command -v ollama &> /dev/null; then
    echo -e "${GREEN}✅ Ollama найдена${NC}"

    # Проверяем, запущена ли Ollama
    if ! pgrep -x "ollama" > /dev/null; then
        echo -e "${YELLOW}🖥️  Запуск Ollama сервера...${NC}"
        ollama serve > /dev/null 2>&1 &
        sleep 2

        if pgrep -x "ollama" > /dev/null; then
            echo -e "${GREEN}✅ Ollama сервер запущен на http://localhost:11434${NC}"
        else
            echo -e "${RED}❌ Не удалось запустить Ollama${NC}"
        fi
    else
        echo -e "${GREEN}✅ Ollama уже запущена${NC}"
    fi

    # Проверяем наличие модели llama3.1:8b
    if ollama list | grep -q "llama3.1:8b"; then
        echo -e "${GREEN}✅ Модель llama3.1:8b установлена${NC}"
    else
        echo -e "${YELLOW}⚠️  Модель llama3.1:8b не найдена${NC}"
        echo -e "${YELLOW}   Установите: ollama pull llama3.1:8b${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  Ollama не установлена (работа продолжится с облачными API)${NC}"
    echo -e "${YELLOW}   Установите для бесплатной генерации: brew install ollama${NC}"
fi

echo "═══════════════════════════════════════════════════════════"

# 2. Проверка Python окружения
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}📦 Создание виртуального окружения...${NC}"
    python3 -m venv venv
fi

echo -e "${GREEN}🐍 Активация Python окружения...${NC}"
source venv/bin/activate

# 3. Установка зависимостей (если нужно)
if [ ! -f "venv/dependencies_installed" ]; then
    echo -e "${YELLOW}📦 Установка Python зависимостей...${NC}"
    pip install -r requirements.txt
    touch venv/dependencies_installed
fi

echo "═══════════════════════════════════════════════════════════"

# 4. Запуск Flask API
echo -e "${GREEN}🌐 Запуск Flask API сервера (порт 5001)...${NC}"
cd api
python server.py > ../logs/api.log 2>&1 &
API_PID=$!
cd ..

sleep 3

if ps -p $API_PID > /dev/null; then
    echo -e "${GREEN}✅ Flask API запущен (PID: $API_PID)${NC}"
else
    echo -e "${RED}❌ Не удалось запустить Flask API${NC}"
    exit 1
fi

echo "═══════════════════════════════════════════════════════════"

# 5. Запуск Electron Desktop приложения
echo -e "${GREEN}🖥️  Запуск Desktop приложения...${NC}"
cd youtube-automation-app

# Установка npm зависимостей (если нужно)
if [ ! -d "node_modules" ]; then
    echo -e "${YELLOW}📦 Установка npm зависимостей...${NC}"
    npm install
fi

# Запуск Electron
npm start

# 6. Cleanup при выходе
echo ""
echo "═══════════════════════════════════════════════════════════"
echo -e "${YELLOW}🛑 Остановка серверов...${NC}"

# Остановить Flask API
if ps -p $API_PID > /dev/null; then
    kill $API_PID
    echo -e "${GREEN}✅ Flask API остановлен${NC}"
fi

# Опционально: остановить Ollama (закомментировано, т.к. может использоваться другими приложениями)
# if pgrep -x "ollama" > /dev/null; then
#     killall ollama
#     echo -e "${GREEN}✅ Ollama остановлена${NC}"
# fi

echo -e "${GREEN}👋 YouTube Automation Studio остановлен${NC}"
echo "═══════════════════════════════════════════════════════════"
