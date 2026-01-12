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

    // Update images estimate
    if (typeof updateImagesEstimate === 'function') {
        updateImagesEstimate();
    }
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
// IMAGES BLOCK
// ═══════════════════════════════════════════════════════════════

let references = []; // Массив референсов
let currentReferenceType = null; // 'character' или 'style'

function initImages() {
    // Обновление оценки количества изображений
    const distributionRadios = document.querySelectorAll('input[name="image-distribution"]');
    distributionRadios.forEach(radio => {
        radio.addEventListener('change', updateImagesEstimate);
    });

    // Кнопки добавления референсов
    document.getElementById('add-character-btn').addEventListener('click', () => {
        currentReferenceType = 'character';
        document.getElementById('reference-file-input').click();
    });

    document.getElementById('add-style-btn').addEventListener('click', () => {
        currentReferenceType = 'style';
        document.getElementById('reference-file-input').click();
    });

    // Загрузка референса
    document.getElementById('reference-file-input').addEventListener('change', handleReferenceUpload);

    // Кнопка запуска генерации
    const generateBtn = document.getElementById('start-generation-btn');
    if (generateBtn) {
        generateBtn.addEventListener('click', generateImagesForVideo);
        addLog('info', '🚀 Кнопка генерации подключена');
    }

    // Начальная оценка
    updateImagesEstimate();
}

function updateImagesEstimate() {
    const text = document.getElementById('scenario-input').value;
    if (!text) {
        document.getElementById('images-count-estimate').textContent = 'Примерно будет создано: ~0 изображений';
        return;
    }

    // Подсчёт предложений (примерный - по точкам, вопросам, восклицаниям)
    const sentences = text.split(/[.!?]+/).filter(s => s.trim().length > 10);
    const sentenceCount = sentences.length;

    // Получить распределение
    const distributionValue = parseInt(document.querySelector('input[name="image-distribution"]:checked').value);

    // Рассчитать количество изображений
    const imagesCount = Math.ceil(sentenceCount / distributionValue);

    document.getElementById('images-count-estimate').textContent =
        `Примерно будет создано: ~${imagesCount} изображений`;

    addLog('info', `📊 Оценка: ${imagesCount} изображений (${sentenceCount} предложений / ${distributionValue})`);
}

async function handleReferenceUpload(event) {
    const file = event.target.files[0];
    if (!file) return;

    // Проверка типа файла
    if (!file.type.startsWith('image/')) {
        alert('Пожалуйста, выберите изображение');
        return;
    }

    // Проверка размера (макс 10MB)
    if (file.size > 10 * 1024 * 1024) {
        alert('Файл слишком большой (макс 10MB)');
        return;
    }

    addLog('info', `📎 Загрузка референса: ${file.name}`);

    try {
        // Создать превью
        const imageUrl = await readFileAsDataURL(file);

        // Отправить на сервер
        const formData = new FormData();
        formData.append('file', file);
        formData.append('type', currentReferenceType);

        const response = await fetch('http://localhost:5001/api/upload-reference', {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            throw new Error('Ошибка загрузки на сервер');
        }

        const result = await response.json();

        // Добавить в массив референсов
        const reference = {
            id: result.id,
            type: currentReferenceType,
            name: file.name,
            url: imageUrl,
            serverPath: result.path
        };

        references.push(reference);
        renderReferences();

        addLog('success', `✅ Референс загружен: ${file.name}`);

    } catch (error) {
        addLog('error', `❌ Ошибка загрузки референса: ${error.message}`);
        alert(`Ошибка загрузки:\n${error.message}`);
    }

    // Очистить input
    event.target.value = '';
}

function readFileAsDataURL(file) {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = (e) => resolve(e.target.result);
        reader.onerror = (e) => reject(new Error('Ошибка чтения файла'));
        reader.readAsDataURL(file);
    });
}

function renderReferences() {
    const container = document.getElementById('references-list');

    if (references.length === 0) {
        container.innerHTML = '';
        return;
    }

    container.innerHTML = references.map((ref, index) => `
        <div class="reference-card">
            <img src="${ref.url}" alt="${ref.name}" class="reference-image">
            <div class="reference-info">
                <div class="reference-type">${ref.type === 'character' ? '👤 Персонаж' : '🎨 Стиль'}</div>
                <div class="reference-name">${ref.name}</div>
            </div>
            <button class="reference-remove" onclick="removeReference(${index})">✕</button>
        </div>
    `).join('');
}

function removeReference(index) {
    const ref = references[index];

    if (confirm(`Удалить референс "${ref.name}"?`)) {
        // Удалить с сервера
        fetch(`http://localhost:5001/api/delete-reference/${ref.id}`, {
            method: 'DELETE'
        }).catch(err => console.error('Ошибка удаления с сервера:', err));

        // Удалить из массива
        references.splice(index, 1);
        renderReferences();

        addLog('info', `🗑️ Референс удалён: ${ref.name}`);
    }
}

// ═══════════════════════════════════════════════════════════════
// IMAGE GENERATION
// ═══════════════════════════════════════════════════════════════

let currentScenes = [];

function generateScenesStructure(scenario, distribution, globalStyle) {
    /**
     * ЗАГЛУШКА: Разбивает сценарий на сцены
     * ПОЗЖЕ: Будет использовать OpenRouter API
     *
     * @param {string} scenario - текст сценария
     * @param {number} distribution - 1, 2 или 3 предложения на сцену
     * @param {string} globalStyle - базовый стиль
     * @returns {Array} массив сцен
     */

    // Разбить на предложения
    const sentences = scenario
        .split(/[.!?]+/)
        .map(s => s.trim())
        .filter(s => s.length > 10);

    const scenes = [];
    const dist = parseInt(distribution);

    for (let i = 0; i < sentences.length; i += dist) {
        const sceneText = sentences
            .slice(i, i + dist)
            .join('. ') + '.';

        // ЗАГЛУШКА: Простая генерация промпта
        // ПОЗЖЕ: OpenRouter API создаст визуальный промпт
        const imagePrompt = sceneText.substring(0, 100) + (globalStyle ? `, ${globalStyle}` : '');

        scenes.push({
            scene_id: scenes.length + 1,
            text: sceneText,
            visual_meaning: `Визуализация сцены ${scenes.length + 1}`,
            image_prompt: imagePrompt,
            emotion: 'neutral',
            camera_motion: 'static'
        });
    }

    return scenes;
}

function splitIntoScenes(text, distributionValue) {
    /**
     * Разбить сценарий на сцены для генерации изображений
     * @param {string} text - Текст сценария
     * @param {number} distributionValue - Количество предложений на 1 изображение (1, 2, или 3)
     * @returns {Array} - Массив сцен [{text: "...", index: 0}, ...]
     */

    if (!text || !text.trim()) {
        return [];
    }

    // Разбить на предложения
    const sentences = text.split(/[.!?]+/).filter(s => s.trim().length > 10);

    // Группировать предложения по distributionValue
    const scenes = [];
    for (let i = 0; i < sentences.length; i += distributionValue) {
        const sceneSentences = sentences.slice(i, i + distributionValue);
        const sceneText = sceneSentences.join('. ').trim() + '.';

        scenes.push({
            index: scenes.length,
            text: sceneText,
            sentences: sceneSentences
        });
    }

    return scenes;
}

async function generateImagesForVideo() {
    /**
     * ОБНОВЛЁННАЯ версия с генерацией сцен
     */

    try {
        // 1. Получить сценарий
        const scenarioText = document.getElementById('scenario-input').value;
        if (!scenarioText || !scenarioText.trim()) {
            alert('⚠️ Сначала введите сценарий');
            return;
        }

        addLog('info', '🚀 Запуск генерации видео...');

        // 2. Получить настройки
        const distributionValue = parseInt(document.querySelector('input[name="image-distribution"]:checked').value);
        const globalStyle = document.getElementById('global-style-input').value || '';
        const promptMode = document.querySelector('input[name="prompt-mode"]:checked').value;
        const imageService = document.querySelector('input[name="image-service"]:checked').value;
        const useReferences = document.getElementById('use-references').checked;
        const autoDownload = document.getElementById('auto-download').checked;
        const whiskRetries = parseInt(document.getElementById('whisk-retries').value);
        const retryDelay = parseInt(document.getElementById('retry-delay').value);

        // 3. Генерация структуры сцен
        addLog('info', '🎬 Генерация структуры сцен...');
        currentScenes = generateScenesStructure(scenarioText, distributionValue, globalStyle);

        if (currentScenes.length === 0) {
            alert('⚠️ Не удалось разбить сценарий на сцены');
            return;
        }

        addLog('success', `✅ Создано сцен: ${currentScenes.length}`);

        // Показать кнопку "Показать сцены"
        document.getElementById('show-scenes-btn').style.display = 'inline-flex';

        // 4. Подготовить referencer
        const referencePaths = useReferences ? references.map(ref => ref.serverPath) : [];

        if (useReferences && referencePaths.length > 0) {
            addLog('info', `📎 Использую ${referencePaths.length} референсов`);
        }

        // 5. Отправить запрос на backend
        addLog('info', `🎨 Генерация ${currentScenes.length} изображений...`);
        addLog('info', `🚀 Сервис: ${imageService === 'whisk' ? 'Whisk AI' : 'Telegram Bot'}`);

        const response = await fetch('http://localhost:5001/api/generate-images', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                scenes: currentScenes,
                global_style: globalStyle,
                prompt_mode: promptMode,
                service: imageService,
                references: referencePaths,
                auto_download: autoDownload,
                whisk_retries: whiskRetries,
                retry_delay: retryDelay
            })
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || 'Ошибка генерации изображений');
        }

        const result = await response.json();

        // 6. Обработать результат
        addLog('success', `✅ Генерация завершена!`);
        addLog('info', `📊 Создано изображений: ${result.images.length}`);
        addLog('info', `⏱️ Общее время: ${result.stats.total_time}с`);
        addLog('info', `📁 Папка с результатами: ${result.output_dir}`);

        // Обновить информацию о проекте
        document.getElementById('info-images').textContent = `${result.images.length} шт`;

        alert(`✅ Генерация завершена!\n\nСоздано изображений: ${result.images.length}\nВремя: ${result.stats.total_time}с`);

    } catch (error) {
        addLog('error', `❌ Ошибка генерации: ${error.message}`);
        alert(`❌ Ошибка генерации:\n${error.message}`);
        console.error('Generation error:', error);
    }
}

// ═══════════════════════════════════════════════════════════════
// СЦЕНЫ - МОДАЛЬНОЕ ОКНО
// ═══════════════════════════════════════════════════════════════

function showScenesModal() {
    /**
     * Показать модальное окно со сценами
     */

    const modal = document.getElementById('scenes-modal');
    const scenesList = document.getElementById('scenes-list');
    const scenesCount = document.getElementById('scenes-count');

    if (!currentScenes || currentScenes.length === 0) {
        alert('Сначала введите сценарий и нажмите кнопку генерации');
        return;
    }

    // Обновить счётчик
    scenesCount.textContent = currentScenes.length;

    // Очистить список
    scenesList.innerHTML = '';

    // Добавить сцены
    currentScenes.forEach(scene => {
        const sceneCard = document.createElement('div');
        sceneCard.className = 'scene-card';

        sceneCard.innerHTML = `
            <div class="scene-header">
                <div class="scene-number">${scene.scene_id}</div>
                <h3 class="scene-title">Сцена ${scene.scene_id}</h3>
            </div>

            <div class="scene-field">
                <div class="scene-field-label">Текст озвучки</div>
                <div class="scene-field-value">${scene.text}</div>
            </div>

            <div class="scene-field">
                <div class="scene-field-label">Визуальный смысл</div>
                <div class="scene-field-value">${scene.visual_meaning}</div>
            </div>

            <div class="scene-field">
                <div class="scene-field-label">Промпт изображения</div>
                <div class="scene-field-value scene-prompt">${scene.image_prompt}</div>
            </div>
        `;

        scenesList.appendChild(sceneCard);
    });

    // Показать модальное окно
    modal.style.display = 'flex';
}

function closeScenesModal() {
    const modal = document.getElementById('scenes-modal');
    modal.style.display = 'none';
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
// ELEVENLABS VOICES
// ═══════════════════════════════════════════════════════════════

let availableVoices = [];
let selectedVoiceId = null;
let currentFilter = 'all';

async function initVoicesSection() {
    /**
     * Инициализация раздела озвучки
     */

    const loadingState = document.getElementById('voices-loading');
    const errorState = document.getElementById('voices-error');
    const filtersSection = document.getElementById('voices-filters');
    const listSection = document.getElementById('voices-list');
    const previewSection = document.getElementById('voices-preview-section');

    try {
        // Показать загрузку
        loadingState.style.display = 'block';
        errorState.style.display = 'none';

        // Загрузить голоса
        const success = await loadVoices();

        if (success && availableVoices.length > 0) {
            // Скрыть загрузку
            loadingState.style.display = 'none';

            // Показать интерфейс
            filtersSection.style.display = 'block';
            listSection.style.display = 'block';
            previewSection.style.display = 'block';

            // Обновить счётчики
            updateVoicesCounts();

            // Отрисовать голоса
            renderVoices();

            // Выбрать первый голос по умолчанию
            if (availableVoices.length > 0) {
                selectVoice(availableVoices[0].voice_id);
            }
        } else {
            // Показать ошибку
            loadingState.style.display = 'none';
            errorState.style.display = 'block';
        }

    } catch (error) {
        console.error('Ошибка инициализации голосов:', error);
        loadingState.style.display = 'none';
        errorState.style.display = 'block';
    }
}

async function loadVoices() {
    /**
     * Загрузить список голосов с бэкенда
     */

    try {
        addLog('info', '🎙️ Загрузка голосов ElevenLabs...');

        const response = await fetch('http://localhost:5001/api/voices');
        const data = await response.json();

        if (data.success) {
            availableVoices = data.voices;

            addLog('success', `✅ Загружено голосов: ${data.voices.length}`);

            const maleCount = data.voices.filter(v => v.gender === 'male').length;
            const femaleCount = data.voices.filter(v => v.gender === 'female').length;

            addLog('info', `   Мужских: ${maleCount}, Женских: ${femaleCount}`);

            return true;
        } else {
            addLog('error', '❌ Ошибка загрузки голосов');
            return false;
        }
    } catch (error) {
        addLog('error', `❌ ${error.message}`);
        return false;
    }
}

function updateVoicesCounts() {
    /**
     * Обновить счётчики в фильтрах
     */

    const totalCount = availableVoices.length;
    const maleCount = availableVoices.filter(v => v.gender === 'male').length;
    const femaleCount = availableVoices.filter(v => v.gender === 'female').length;

    document.getElementById('count-all').textContent = totalCount;
    document.getElementById('count-male').textContent = maleCount;
    document.getElementById('count-female').textContent = femaleCount;
}

function renderVoices(filter = 'all') {
    /**
     * Отрисовать карточки голосов
     */

    const grid = document.getElementById('voices-grid');
    grid.innerHTML = '';

    // Фильтрация
    let filtered = availableVoices;
    if (filter === 'male') {
        filtered = availableVoices.filter(v => v.gender === 'male');
    } else if (filter === 'female') {
        filtered = availableVoices.filter(v => v.gender === 'female');
    }

    // Отрисовка
    filtered.forEach(voice => {
        const card = createVoiceCard(voice);
        grid.appendChild(card);
    });
}

function createVoiceCard(voice) {
    /**
     * Создать карточку голоса
     */

    const card = document.createElement('div');
    card.className = 'voice-card';
    card.dataset.voiceId = voice.voice_id;

    if (voice.voice_id === selectedVoiceId) {
        card.classList.add('selected');
    }

    // Иконка гендера
    const genderIcon = voice.gender === 'male' ? '👨' :
                      voice.gender === 'female' ? '👩' : '👤';

    // Лейблы
    const labels = voice.labels || {};
    const labelHTML = Object.entries(labels)
        .slice(0, 3)
        .map(([key, val]) => `<span class="voice-label">${val}</span>`)
        .join('');

    card.innerHTML = `
        <div class="voice-card-header">
            <h4 class="voice-name">${voice.name}</h4>
            <span class="voice-gender">${genderIcon}</span>
        </div>

        <div class="voice-labels">
            ${labelHTML}
        </div>

        <div class="voice-actions">
            <button class="voice-play-btn" onclick="playVoicePreview('${voice.voice_id}')">
                ▶️ Прослушать
            </button>
        </div>
    `;

    // Клик по карточке = выбор голоса
    card.addEventListener('click', (e) => {
        if (!e.target.classList.contains('voice-play-btn')) {
            selectVoice(voice.voice_id);
        }
    });

    return card;
}

function selectVoice(voiceId) {
    /**
     * Выбрать голос
     */

    selectedVoiceId = voiceId;

    // Обновить UI
    document.querySelectorAll('.voice-card').forEach(card => {
        if (card.dataset.voiceId === voiceId) {
            card.classList.add('selected');
        } else {
            card.classList.remove('selected');
        }
    });

    const voice = availableVoices.find(v => v.voice_id === voiceId);
    if (voice) {
        addLog('info', `✅ Выбран голос: ${voice.name}`);
    }
}

function playVoicePreview(voiceId) {
    /**
     * Воспроизвести preview голоса
     */

    const audio = new Audio(`http://localhost:5001/api/voices/${voiceId}/preview`);

    audio.play().catch(error => {
        console.error('Ошибка воспроизведения:', error);
        addLog('error', '❌ Preview не найден. Сгенерируйте preview сначала.');
    });

    const voice = availableVoices.find(v => v.voice_id === voiceId);
    addLog('info', `▶️ ${voice ? voice.name : 'Голос'}`);
}

async function generateAllPreviews() {
    /**
     * Генерация preview для всех голосов
     */

    const btn = document.getElementById('generate-previews-btn');
    btn.disabled = true;
    btn.innerHTML = '<span class="spinner"></span> Генерация...';

    try {
        addLog('info', '🎙️ Генерация preview...');
        addLog('info', '⏳ Это займёт несколько минут...');

        const response = await fetch('http://localhost:5001/api/voices/generate-previews', {
            method: 'POST'
        });

        const data = await response.json();

        if (data.success) {
            addLog('success', `✅ Preview готовы!`);
            addLog('success', `   Успешно: ${data.stats.successful}/${data.stats.total}`);

            if (data.stats.failed > 0) {
                addLog('warning', `   ⚠️ Ошибки: ${data.stats.failed}`);
            }
        } else {
            addLog('error', '❌ Ошибка генерации');
        }

    } catch (error) {
        addLog('error', `❌ ${error.message}`);
    } finally {
        btn.disabled = false;
        btn.innerHTML = '<span class="btn-icon">🎵</span><span class="btn-text">Сгенерировать preview</span>';
    }
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
    initImages(); // Initialize images block

    // Кнопка "Показать сцены"
    const showScenesBtn = document.getElementById('show-scenes-btn');
    if (showScenesBtn) {
        showScenesBtn.addEventListener('click', showScenesModal);
    }

    // Закрытие модального окна
    const closeButtons = document.querySelectorAll('#close-scenes-modal, #close-scenes-modal-btn');
    closeButtons.forEach(btn => {
        btn.addEventListener('click', closeScenesModal);
    });

    // Закрытие по клику на оверлей
    const modalOverlay = document.querySelector('#scenes-modal .modal-overlay');
    if (modalOverlay) {
        modalOverlay.addEventListener('click', closeScenesModal);
    }

    // Инициализация голосов
    initVoicesSection();

    // Фильтры голосов
    document.querySelectorAll('.filter-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');

            const filter = btn.dataset.filter;
            renderVoices(filter);
        });
    });

    // Кнопка генерации preview
    const generatePreviewsBtn = document.getElementById('generate-previews-btn');
    if (generatePreviewsBtn) {
        generatePreviewsBtn.addEventListener('click', generateAllPreviews);
    }

    // Кнопка повтора загрузки голосов
    const retryBtn = document.getElementById('retry-voices-btn');
    if (retryBtn) {
        retryBtn.addEventListener('click', initVoicesSection);
    }

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
