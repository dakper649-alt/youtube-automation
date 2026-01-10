/* ═══════════════════════════════════════════════════════════════
   YOUTUBE AUTOMATION STUDIO - MAIN APPLICATION LOGIC
   ═══════════════════════════════════════════════════════════════ */

// ═══════════════════════════════════════════════════════════════
// NAVIGATION SYSTEM
// ═══════════════════════════════════════════════════════════════

function initNavigation() {
    const navButtons = document.querySelectorAll('.nav-btn');

    navButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            const section = btn.dataset.section;
            switchSection(section);
        });
    });
}

function switchSection(sectionName) {
    // Remove active from all nav buttons
    document.querySelectorAll('.nav-btn').forEach(btn => {
        btn.classList.remove('active');
    });

    // Add active to clicked button
    const activeBtn = document.querySelector(`.nav-btn[data-section="${sectionName}"]`);
    if (activeBtn) {
        activeBtn.classList.add('active');
    }

    // Hide all sections
    document.querySelectorAll('.content-section').forEach(section => {
        section.classList.remove('active');
    });

    // Show selected section
    const activeSection = document.getElementById(`${sectionName}-section`);
    if (activeSection) {
        activeSection.classList.add('active');
    }

    // Log to console
    addLog('info', `Переключено на: ${getSectionName(sectionName)}`);
}

function getSectionName(sectionId) {
    const names = {
        'generation': 'Генерация видео',
        'queue': 'Очередь генерации',
        'export': 'Выгрузка видео',
        'stats': 'Статистика',
        'settings': 'Настройки'
    };
    return names[sectionId] || sectionId;
}

// ═══════════════════════════════════════════════════════════════
// SCENARIO STATS & DETECTION
// ═══════════════════════════════════════════════════════════════

function initScenarioField() {
    const textarea = document.getElementById('scenario-input');

    if (textarea) {
        // Update stats on input
        textarea.addEventListener('input', updateScenarioStats);

        // Initial update
        updateScenarioStats();
    }
}

function updateScenarioStats() {
    const textarea = document.getElementById('scenario-input');
    const text = textarea.value;

    // Character count
    const charCount = text.length;
    document.getElementById('char-count').textContent = `${charCount.toLocaleString()} символов`;

    // Language detection
    const language = detectLanguage(text);
    document.getElementById('lang-detected').textContent = `Язык: ${language}`;

    // Duration calculation (900-1000 chars per minute, average 950)
    const durationMin = Math.round(charCount / 950);
    document.getElementById('duration-calc').textContent = `~${durationMin} мин`;

    // Update project info panel
    document.getElementById('info-language').textContent = language;
}

function detectLanguage(text) {
    if (!text || text.length < 10) return '-';

    // Подсчёт символов разных алфавитов
    const cyrillicCount = (text.match(/[а-яёА-ЯЁ]/g) || []).length;
    const latinCount = (text.match(/[a-zA-Z]/g) || []).length;
    const chineseCount = (text.match(/[\u4e00-\u9fa5]/g) || []).length;
    const japaneseCount = (text.match(/[\u3040-\u309f\u30a0-\u30ff]/g) || []).length;
    const koreanCount = (text.match(/[\uac00-\ud7af]/g) || []).length;
    const arabicCount = (text.match(/[\u0600-\u06ff]/g) || []).length;
    const hebrewCount = (text.match(/[\u0590-\u05ff]/g) || []).length;
    const thaiCount = (text.match(/[\u0e00-\u0e7f]/g) || []).length;
    const hindiCount = (text.match(/[\u0900-\u097f]/g) || []).length;

    // Определение языка по максимальному количеству специфичных символов
    const counts = {
        'Китайский (ZH)': chineseCount,
        'Японский (JA)': japaneseCount,
        'Корейский (KO)': koreanCount,
        'Арабский (AR)': arabicCount,
        'Иврит (HE)': hebrewCount,
        'Тайский (TH)': thaiCount,
        'Хинди (HI)': hindiCount
    };

    // Найти максимум среди неевропейских языков
    let maxLang = null;
    let maxCount = 0;

    for (const [lang, count] of Object.entries(counts)) {
        if (count > maxCount && count > 5) { // минимум 5 символов
            maxCount = count;
            maxLang = lang;
        }
    }

    // Если найден неевропейский язык - вернуть его
    if (maxLang) {
        return maxLang;
    }

    // Проверка кириллицы (русский/украинский)
    if (cyrillicCount > latinCount && cyrillicCount > 10) {
        // Украинские буквы (і, ї, є, ґ)
        const ukrainianChars = (text.match(/[іїєґІЇЄҐ]/g) || []).length;
        if (ukrainianChars > 2) {
            return 'Украинский (UK)';
        }
        return 'Русский (RU)';
    }

    // Проверка латиницы (европейские языки)
    if (latinCount > 10) {
        // Испанский (ñ, á, é, í, ó, ú, ¿, ¡)
        const spanishChars = (text.match(/[ñáéíóúÑÁÉÍÓÚ¿¡]/g) || []).length;
        if (spanishChars > 2) {
            return 'Испанский (ES)';
        }

        // Французский (è, é, ê, ë, à, â, ç, ù, î, ô)
        const frenchChars = (text.match(/[èéêëàâçùîôÈÉÊËÀÂÇÙÎÔ]/g) || []).length;
        if (frenchChars > 2) {
            return 'Французский (FR)';
        }

        // Немецкий (ä, ö, ü, ß)
        const germanChars = (text.match(/[äöüßÄÖÜ]/g) || []).length;
        if (germanChars > 2) {
            return 'Немецкий (DE)';
        }

        // Португальский (ã, õ, â, ê, ô, ç)
        const portugueseChars = (text.match(/[ãõâêôçÃÕÂÊÔÇ]/g) || []).length;
        if (portugueseChars > 2) {
            return 'Португальский (PT)';
        }

        // Итальянский (à, è, é, ì, ò, ù)
        const italianChars = (text.match(/[àèéìòùÀÈÉÌÒÙ]/g) || []).length;
        if (italianChars > 2) {
            return 'Итальянский (IT)';
        }

        // Польский (ą, ć, ę, ł, ń, ó, ś, ź, ż)
        const polishChars = (text.match(/[ąćęłńóśźżĄĆĘŁŃÓŚŹŻ]/g) || []).length;
        if (polishChars > 2) {
            return 'Польский (PL)';
        }

        // По умолчанию - английский
        return 'Английский (EN)';
    }

    return 'Не определён';
}

// ═══════════════════════════════════════════════════════════════
// FILE IMPORT (TXT + DOCX)
// ═══════════════════════════════════════════════════════════════

function initFileImport() {
    const importBtn = document.getElementById('import-btn');
    const fileInput = document.getElementById('file-input');

    if (importBtn && fileInput) {
        importBtn.addEventListener('click', () => {
            fileInput.click();
        });

        fileInput.addEventListener('change', handleFileImport);
    }
}

async function handleFileImport(event) {
    const file = event.target.files[0];
    if (!file) return;

    addLog('info', `Импорт файла: ${file.name}`);

    try {
        let text = '';

        if (file.name.endsWith('.txt')) {
            text = await readTextFile(file);
        } else if (file.name.endsWith('.docx')) {
            text = await readDocxFile(file);
        } else {
            addLog('error', 'Неподдерживаемый формат файла');
            return;
        }

        // Insert text into textarea
        document.getElementById('scenario-input').value = text;
        updateScenarioStats();

        addLog('success', `Импортировано ${text.length} символов из ${file.name}`);

    } catch (error) {
        console.error('File import error:', error);
        addLog('error', `Ошибка импорта: ${error.message}`);
    }

    // Reset file input
    event.target.value = '';
}

async function readTextFile(file) {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();

        reader.onload = (e) => {
            resolve(e.target.result);
        };

        reader.onerror = (e) => {
            reject(new Error('Ошибка чтения TXT файла'));
        };

        reader.readAsText(file);
    });
}

async function readDocxFile(file) {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();

        reader.onload = async (e) => {
            try {
                const arrayBuffer = e.target.result;

                // Use Mammoth.js to extract text
                const result = await mammoth.extractRawText({ arrayBuffer });

                resolve(result.value);
            } catch (error) {
                reject(new Error('Ошибка чтения DOCX файла'));
            }
        };

        reader.onerror = (e) => {
            reject(new Error('Ошибка чтения DOCX файла'));
        };

        reader.readAsArrayBuffer(file);
    });
}

// ═══════════════════════════════════════════════════════════════
// CLEAR BUTTON
// ═══════════════════════════════════════════════════════════════

function initClearButton() {
    const clearBtn = document.getElementById('clear-btn');

    if (clearBtn) {
        clearBtn.addEventListener('click', () => {
            if (confirm('Очистить поле сценария?')) {
                document.getElementById('scenario-input').value = '';
                updateScenarioStats();
                addLog('warning', 'Сценарий очищен');
            }
        });
    }
}

// ═══════════════════════════════════════════════════════════════
// CONSOLE LOGGING SYSTEM
// ═══════════════════════════════════════════════════════════════

const MAX_LOG_ENTRIES = 100;

function addLog(type, message) {
    const consoleLog = document.getElementById('console-log');
    if (!consoleLog) return;

    // Create log entry
    const entry = document.createElement('div');
    entry.className = `log-entry ${type}`;

    // Format timestamp
    const now = new Date();
    const time = now.toLocaleTimeString('ru-RU', {
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
    });

    // Set content
    entry.innerHTML = `
        <span class="log-time">${time}</span>
        <span class="log-text">${escapeHtml(message)}</span>
    `;

    // Add to console
    consoleLog.appendChild(entry);

    // Auto-scroll to bottom
    consoleLog.scrollTop = consoleLog.scrollHeight;

    // Limit number of entries
    while (consoleLog.children.length > MAX_LOG_ENTRIES) {
        consoleLog.removeChild(consoleLog.firstChild);
    }
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// ═══════════════════════════════════════════════════════════════
// PROJECT INFO PANEL
// ═══════════════════════════════════════════════════════════════

function initProjectInfo() {
    // Set default values
    document.getElementById('info-language').textContent = '-';
    document.getElementById('info-voice').textContent = '-';
    document.getElementById('info-images').textContent = '-';
    document.getElementById('info-resolution').textContent = '1920x1080';
}

// ═══════════════════════════════════════════════════════════════
// INITIALIZATION
// ═══════════════════════════════════════════════════════════════

window.addEventListener('DOMContentLoaded', () => {
    // Initialize all modules
    initNavigation();
    initScenarioField();
    initFileImport();
    initClearButton();
    initProjectInfo();

    // Welcome log
    addLog('success', 'YouTube Automation Studio запущен');
    addLog('info', 'Готов к работе. Начните с создания сценария.');

    // Check backend health
    checkBackendHealth();
});

async function checkBackendHealth() {
    try {
        const response = await fetch('http://localhost:5001/api/health', {
            method: 'GET'
        });

        if (response.ok) {
            addLog('success', 'Подключение к Flask API: OK');
        } else {
            addLog('warning', 'Flask API отвечает с ошибкой');
        }
    } catch (error) {
        addLog('warning', 'Flask API недоступен (порт 5001)');
        console.warn('Backend health check failed:', error);
    }
}

// ═══════════════════════════════════════════════════════════════
// BACKEND READY LISTENER (ELECTRON)
// ═══════════════════════════════════════════════════════════════

if (window.electronAPI) {
    window.electronAPI.onBackendReady(() => {
        addLog('success', 'Backend сервер готов');
    });
}
