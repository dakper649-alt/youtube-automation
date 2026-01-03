// ═══════════════════════════════════════════════════════════════
// SETTINGS PAGE LOGIC
// ═══════════════════════════════════════════════════════════════

// Settings state
let currentSettings = {};

// ═══════════════════════════════════════════════════════════════
// INITIALIZATION
// ═══════════════════════════════════════════════════════════════

document.addEventListener('DOMContentLoaded', async () => {
    console.log('⚙️ Settings page initialized');

    // Setup tab switching
    setupTabs();

    // Setup back button
    setupBackButton();

    // Load current settings
    await loadSettings();

    // Load API keys
    await loadAPIKeys();

    // Setup event listeners
    setupEventListeners();

    // Populate dropdowns from app.js constants
    populateDropdowns();
});

// ═══════════════════════════════════════════════════════════════
// TAB SWITCHING
// ═══════════════════════════════════════════════════════════════

function setupTabs() {
    const tabs = document.querySelectorAll('.tab');
    const tabPanels = document.querySelectorAll('.tab-panel');

    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            // Remove active class from all tabs and panels
            tabs.forEach(t => t.classList.remove('active'));
            tabPanels.forEach(panel => panel.classList.remove('active'));

            // Add active class to clicked tab
            tab.classList.add('active');

            // Show corresponding panel
            const tabName = tab.getAttribute('data-tab');
            const panel = document.getElementById(`${tabName}-tab`);
            if (panel) {
                panel.classList.add('active');
            }
        });
    });
}

// ═══════════════════════════════════════════════════════════════
// NAVIGATION
// ═══════════════════════════════════════════════════════════════

function setupBackButton() {
    const backBtn = document.getElementById('back-btn');
    if (backBtn) {
        backBtn.addEventListener('click', () => {
            window.location.href = 'index.html';
        });
    }
}

// ═══════════════════════════════════════════════════════════════
// LOAD SETTINGS
// ═══════════════════════════════════════════════════════════════

async function loadSettings() {
    try {
        const response = await fetch('http://localhost:5001/api/settings');

        if (response.ok) {
            currentSettings = await response.json();
            applySettings(currentSettings);
            console.log('✅ Settings loaded:', currentSettings);
        } else {
            console.warn('⚠️ Failed to load settings, using defaults');
            applyDefaultSettings();
        }
    } catch (error) {
        console.error('❌ Error loading settings:', error);
        applyDefaultSettings();
    }
}

function applySettings(settings) {
    // General settings
    if (settings.outputFolder) {
        document.getElementById('output-folder').value = settings.outputFolder;
    }
    if (settings.autoCleanup !== undefined) {
        document.getElementById('auto-cleanup').checked = settings.autoCleanup;
    }
    if (settings.language) {
        document.getElementById('language').value = settings.language;
    }

    // Generation settings
    if (settings.defaultStyle) {
        document.getElementById('default-style').value = settings.defaultStyle;
    }
    if (settings.defaultVoice) {
        document.getElementById('default-voice').value = settings.defaultVoice;
    }
    if (settings.defaultMusic) {
        document.getElementById('default-music').value = settings.defaultMusic;
    }
    if (settings.musicEnabled !== undefined) {
        document.getElementById('music-enabled').checked = settings.musicEnabled;
    }
    if (settings.defaultLength) {
        document.getElementById('default-length').value = settings.defaultLength;
    }

    // Telegram settings
    if (settings.telegramToken) {
        document.getElementById('telegram-token').value = settings.telegramToken;
    }
    if (settings.telegramChatId) {
        document.getElementById('telegram-chat-id').value = settings.telegramChatId;
    }
    if (settings.notifyStart !== undefined) {
        document.getElementById('notify-start').checked = settings.notifyStart;
    }
    if (settings.notifyProgress !== undefined) {
        document.getElementById('notify-progress').checked = settings.notifyProgress;
    }
    if (settings.notifyComplete !== undefined) {
        document.getElementById('notify-complete').checked = settings.notifyComplete;
    }
    if (settings.notifyError !== undefined) {
        document.getElementById('notify-error').checked = settings.notifyError;
    }

    // Appearance settings
    if (settings.theme) {
        applyTheme(settings.theme);
    }
    if (settings.fontSize) {
        document.getElementById('font-size').value = settings.fontSize;
    }
    if (settings.animationsEnabled !== undefined) {
        document.getElementById('animations-enabled').checked = settings.animationsEnabled;
    }
}

function applyDefaultSettings() {
    currentSettings = {
        outputFolder: '~/Desktop/YouTube_Videos',
        autoCleanup: true,
        language: 'ru',
        defaultStyle: 'minimalist_stick_figure',
        defaultVoice: 'rachel',
        defaultMusic: 'calm_piano',
        musicEnabled: true,
        defaultLength: '1200',
        telegramToken: '',
        telegramChatId: '',
        notifyStart: true,
        notifyProgress: true,
        notifyComplete: true,
        notifyError: true,
        theme: 'dark',
        fontSize: 'medium',
        animationsEnabled: true
    };
    applySettings(currentSettings);
}

// ═══════════════════════════════════════════════════════════════
// LOAD API KEYS
// ═══════════════════════════════════════════════════════════════

async function loadAPIKeys() {
    try {
        const response = await fetch('http://localhost:5001/api/settings/keys');

        if (!response.ok) {
            throw new Error('Failed to load API keys');
        }

        const data = await response.json();

        // Update Hugging Face keys
        updateAPISection('hf', data.huggingface || { keys: [], active: 0, requests: 0 });

        // Update ElevenLabs keys
        updateAPISection('elevenlabs', data.elevenlabs || { keys: [], active: 0, requests: 0 });

        // Update YouTube keys
        updateAPISection('youtube', data.youtube || { keys: [], active: 0, requests: 0 });

        // Update Groq keys
        updateAPISection('groq', data.groq || { keys: [], active: 0, requests: 0 });

        console.log('✅ API keys loaded');
    } catch (error) {
        console.error('❌ Error loading API keys:', error);

        // Show error in all sections
        ['hf', 'elevenlabs', 'youtube', 'groq'].forEach(service => {
            const listElement = document.getElementById(`${service}-keys-list`);
            if (listElement) {
                listElement.innerHTML = '<p class="loading">❌ Ошибка загрузки ключей</p>';
            }
        });
    }
}

function updateAPISection(service, data) {
    // Update stats
    const activeElement = document.getElementById(`${service}-active`);
    const requestsElement = document.getElementById(`${service}-requests`);

    if (activeElement) {
        activeElement.textContent = data.active || 0;
    }
    if (requestsElement) {
        requestsElement.textContent = data.requests || 0;
    }

    // Update keys list
    const listElement = document.getElementById(`${service}-keys-list`);
    if (!listElement) return;

    if (!data.keys || data.keys.length === 0) {
        listElement.innerHTML = '<p class="loading">Ключи не найдены</p>';
        return;
    }

    listElement.innerHTML = '';

    data.keys.forEach((key, index) => {
        const keyItem = document.createElement('div');
        keyItem.className = 'api-key-item';

        const maskedKey = maskAPIKey(key.value || key);
        const status = key.active !== false ? 'active' : 'inactive';
        const statusText = key.active !== false ? 'Активен' : 'Неактивен';

        keyItem.innerHTML = `
            <div class="key-info">
                <span class="key-value">${maskedKey}</span>
                <span class="key-status ${status}">${statusText}</span>
            </div>
            <div class="key-actions">
                <button onclick="testAPIKey('${service}', ${index})">🔍 Тест</button>
                <button class="delete" onclick="deleteAPIKey('${service}', ${index})">🗑️ Удалить</button>
            </div>
        `;

        listElement.appendChild(keyItem);
    });
}

function maskAPIKey(key) {
    if (!key || key.length < 10) return '***';
    return key.substring(0, 4) + '...' + key.substring(key.length - 4);
}

// ═══════════════════════════════════════════════════════════════
// API KEY ACTIONS
// ═══════════════════════════════════════════════════════════════

async function addKey(service) {
    const key = prompt(`Введите новый API ключ для ${service}:`);
    if (!key) return;

    try {
        const response = await fetch('http://localhost:5001/api/settings/keys/add', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ service, key })
        });

        if (response.ok) {
            alert('✅ Ключ добавлен успешно');
            await loadAPIKeys();
        } else {
            const error = await response.json();
            alert('❌ Ошибка: ' + (error.error || 'Не удалось добавить ключ'));
        }
    } catch (error) {
        console.error('Error adding key:', error);
        alert('❌ Ошибка подключения к серверу');
    }
}

async function testAPIKey(service, index) {
    try {
        const response = await fetch('http://localhost:5001/api/settings/keys/test', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ service, index })
        });

        const result = await response.json();

        if (result.valid) {
            alert('✅ Ключ работает корректно');
        } else {
            alert('❌ Ключ не работает: ' + (result.error || 'Неизвестная ошибка'));
        }
    } catch (error) {
        console.error('Error testing key:', error);
        alert('❌ Ошибка тестирования ключа');
    }
}

async function deleteAPIKey(service, index) {
    if (!confirm('Вы уверены, что хотите удалить этот ключ?')) return;

    try {
        const response = await fetch('http://localhost:5001/api/settings/keys/delete', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ service, index })
        });

        if (response.ok) {
            alert('✅ Ключ удалён');
            await loadAPIKeys();
        } else {
            alert('❌ Ошибка удаления ключа');
        }
    } catch (error) {
        console.error('Error deleting key:', error);
        alert('❌ Ошибка подключения к серверу');
    }
}

// ═══════════════════════════════════════════════════════════════
// SAVE SETTINGS
// ═══════════════════════════════════════════════════════════════

async function saveSettings() {
    const settings = {
        // General
        outputFolder: document.getElementById('output-folder').value,
        autoCleanup: document.getElementById('auto-cleanup').checked,
        language: document.getElementById('language').value,

        // Generation
        defaultStyle: document.getElementById('default-style').value,
        defaultVoice: document.getElementById('default-voice').value,
        defaultMusic: document.getElementById('default-music').value,
        musicEnabled: document.getElementById('music-enabled').checked,
        defaultLength: document.getElementById('default-length').value,

        // Telegram
        telegramToken: document.getElementById('telegram-token').value,
        telegramChatId: document.getElementById('telegram-chat-id').value,
        notifyStart: document.getElementById('notify-start').checked,
        notifyProgress: document.getElementById('notify-progress').checked,
        notifyComplete: document.getElementById('notify-complete').checked,
        notifyError: document.getElementById('notify-error').checked,

        // Appearance
        theme: document.querySelector('.theme-option.active')?.getAttribute('data-theme') || 'dark',
        fontSize: document.getElementById('font-size').value,
        animationsEnabled: document.getElementById('animations-enabled').checked
    };

    try {
        const response = await fetch('http://localhost:5001/api/settings/save', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(settings)
        });

        if (response.ok) {
            alert('✅ Настройки сохранены успешно!');
            currentSettings = settings;
        } else {
            const error = await response.json();
            alert('❌ Ошибка сохранения: ' + (error.error || 'Неизвестная ошибка'));
        }
    } catch (error) {
        console.error('Error saving settings:', error);
        alert('❌ Ошибка подключения к серверу');
    }
}

// ═══════════════════════════════════════════════════════════════
// TELEGRAM TEST
// ═══════════════════════════════════════════════════════════════

async function testTelegram() {
    const token = document.getElementById('telegram-token').value;
    const chatId = document.getElementById('telegram-chat-id').value;

    if (!token || !chatId) {
        alert('⚠️ Введите Bot Token и Chat ID');
        return;
    }

    try {
        const response = await fetch('http://localhost:5001/api/test-telegram', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ token, chatId })
        });

        const result = await response.json();

        if (result.success) {
            alert('✅ Тестовое сообщение отправлено успешно!');
        } else {
            alert('❌ Ошибка отправки: ' + (result.error || 'Неизвестная ошибка'));
        }
    } catch (error) {
        console.error('Error testing Telegram:', error);
        alert('❌ Ошибка подключения к серверу');
    }
}

// ═══════════════════════════════════════════════════════════════
// THEME SWITCHING
// ═══════════════════════════════════════════════════════════════

function setupThemeSelector() {
    const themeOptions = document.querySelectorAll('.theme-option');

    themeOptions.forEach(option => {
        option.addEventListener('click', () => {
            // Remove active from all
            themeOptions.forEach(opt => opt.classList.remove('active'));

            // Add active to clicked
            option.classList.add('active');

            // Apply theme
            const theme = option.getAttribute('data-theme');
            applyTheme(theme);
        });
    });
}

function applyTheme(theme) {
    if (theme === 'light') {
        document.body.classList.add('light-theme');
    } else {
        document.body.classList.remove('light-theme');
    }

    // Update active button
    const themeOptions = document.querySelectorAll('.theme-option');
    themeOptions.forEach(option => {
        if (option.getAttribute('data-theme') === theme) {
            option.classList.add('active');
        } else {
            option.classList.remove('active');
        }
    });
}

// ═══════════════════════════════════════════════════════════════
// EXPORT / IMPORT
// ═══════════════════════════════════════════════════════════════

async function exportSettings() {
    try {
        const response = await fetch('http://localhost:5001/api/settings');
        if (!response.ok) throw new Error('Failed to load settings');

        const settings = await response.json();
        const dataStr = JSON.stringify(settings, null, 2);
        const dataBlob = new Blob([dataStr], { type: 'application/json' });

        const url = URL.createObjectURL(dataBlob);
        const link = document.createElement('a');
        link.href = url;
        link.download = `youtube-automation-settings-${Date.now()}.json`;
        link.click();

        URL.revokeObjectURL(url);

        alert('✅ Настройки экспортированы!');
    } catch (error) {
        console.error('Error exporting settings:', error);
        alert('❌ Ошибка экспорта настроек');
    }
}

async function importSettings() {
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = 'application/json';

    input.onchange = async (e) => {
        const file = e.target.files[0];
        if (!file) return;

        try {
            const text = await file.text();
            const settings = JSON.parse(text);

            // Save imported settings
            const response = await fetch('http://localhost:5001/api/settings/save', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(settings)
            });

            if (response.ok) {
                alert('✅ Настройки импортированы! Перезагрузите страницу.');
                window.location.reload();
            } else {
                alert('❌ Ошибка импорта настроек');
            }
        } catch (error) {
            console.error('Error importing settings:', error);
            alert('❌ Ошибка чтения файла');
        }
    };

    input.click();
}

async function resetSettings() {
    if (!confirm('Вы уверены, что хотите сбросить все настройки?')) return;

    try {
        const response = await fetch('http://localhost:5001/api/settings/reset', {
            method: 'POST'
        });

        if (response.ok) {
            alert('✅ Настройки сброшены! Перезагрузите страницу.');
            window.location.reload();
        } else {
            alert('❌ Ошибка сброса настроек');
        }
    } catch (error) {
        console.error('Error resetting settings:', error);
        alert('❌ Ошибка подключения к серверу');
    }
}

// ═══════════════════════════════════════════════════════════════
// FOLDER SELECTION
// ═══════════════════════════════════════════════════════════════

async function chooseFolder() {
    try {
        const response = await fetch('http://localhost:5001/api/choose-folder', {
            method: 'POST'
        });

        if (response.ok) {
            const result = await response.json();
            if (result.path) {
                document.getElementById('output-folder').value = result.path;
            }
        }
    } catch (error) {
        console.error('Error choosing folder:', error);
        alert('❌ Ошибка выбора папки');
    }
}

// ═══════════════════════════════════════════════════════════════
// POPULATE DROPDOWNS
// ═══════════════════════════════════════════════════════════════

function populateDropdowns() {
    // This will be populated from the same constants as app.js
    // For now, they're already in the HTML, but we could load them dynamically
    // if we want to keep a single source of truth

    console.log('✅ Dropdowns populated from HTML defaults');
}

// ═══════════════════════════════════════════════════════════════
// EVENT LISTENERS
// ═══════════════════════════════════════════════════════════════

function setupEventListeners() {
    // Save settings button
    const saveBtn = document.getElementById('save-settings-btn');
    if (saveBtn) {
        saveBtn.addEventListener('click', saveSettings);
    }

    // Export button
    const exportBtn = document.getElementById('export-settings-btn');
    if (exportBtn) {
        exportBtn.addEventListener('click', exportSettings);
    }

    // Import button
    const importBtn = document.getElementById('import-settings-btn');
    if (importBtn) {
        importBtn.addEventListener('click', importSettings);
    }

    // Reset button
    const resetBtn = document.getElementById('reset-settings-btn');
    if (resetBtn) {
        resetBtn.addEventListener('click', resetSettings);
    }

    // Test Telegram button
    const testTelegramBtn = document.getElementById('test-telegram-btn');
    if (testTelegramBtn) {
        testTelegramBtn.addEventListener('click', testTelegram);
    }

    // Choose folder button
    const chooseFolderBtn = document.getElementById('choose-folder-btn');
    if (chooseFolderBtn) {
        chooseFolderBtn.addEventListener('click', chooseFolder);
    }

    // Theme selector
    setupThemeSelector();

    console.log('✅ Event listeners setup complete');
}
