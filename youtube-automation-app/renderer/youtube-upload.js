// ═══════════════════════════════════════════════════════════════
// YOUTUBE UPLOAD PAGE - JAVASCRIPT
// ═══════════════════════════════════════════════════════════════

// State
let selectedVideo = null;
let currentTags = [];
let selectedTitleVariant = null;

// ═══════════════════════════════════════════════════════════════
// DESCRIPTION TEMPLATES
// ═══════════════════════════════════════════════════════════════

const templates = {
    psychology: `В этом видео мы разберём [тему].

📌 Таймкоды:
0:00 - Введение
0:30 - Основная часть
2:00 - Выводы

👍 Понравилось видео? Поставь лайк и подпишись!
🔔 Включи уведомления, чтобы не пропустить новые видео

#психология #саморазвитие #мотивация`,

    health: `🌿 Всё о [теме] в этом видео!

Сегодня обсудим важные аспекты здоровья и wellness.

📌 Таймкоды:
0:00 - Что это такое
1:00 - Как это работает
2:30 - Практические советы

💚 Подписывайся на канал для большего контента о здоровье!

#здоровье #wellness #ЗОЖ`,

    business: `💼 Бизнес-инсайты о [теме]

В этом видео разбираем стратегии успешных предпринимателей.

📊 Что вы узнаете:
✅ Ключевые принципы
✅ Практические примеры
✅ Пошаговый план действий

🚀 Подпишись для большего бизнес-контента!

#бизнес #предпринимательство #стартап`,

    education: `📚 Образовательное видео о [теме]

Подробный разбор для всех, кто хочет разобраться в теме.

📖 План видео:
1. Теория
2. Практика
3. Примеры

💡 Ставь лайк если было полезно!
📢 Подписывайся на канал!

#образование #обучение #знания`
};

// ═══════════════════════════════════════════════════════════════
// INITIALIZATION
// ═══════════════════════════════════════════════════════════════

window.addEventListener('DOMContentLoaded', () => {
    console.log('YouTube Upload page loaded');

    // Load ready videos
    loadReadyVideos();

    // Setup event listeners
    setupEventListeners();

    // Load draft if exists
    loadDraft();
});

// ═══════════════════════════════════════════════════════════════
// EVENT LISTENERS
// ═══════════════════════════════════════════════════════════════

function setupEventListeners() {
    // Video selection
    const videoSelect = document.getElementById('video-select');
    if (videoSelect) {
        videoSelect.addEventListener('change', (e) => selectVideo(e.target.value));
    }

    // Title generation
    const generateBtn = document.getElementById('generate-titles-btn');
    if (generateBtn) {
        generateBtn.addEventListener('click', generateTitleVariants);
    }

    // Title variant selection
    document.querySelectorAll('input[name="title-choice"]').forEach(radio => {
        radio.addEventListener('change', (e) => {
            if (e.target.value !== 'custom') {
                selectTitleVariant(e.target.value);
            }
        });
    });

    // Custom title input
    const customInput = document.getElementById('custom-title-input');
    if (customInput) {
        customInput.addEventListener('input', updateCustomTitleCounter);
        customInput.addEventListener('focus', () => {
            document.getElementById('title-custom').checked = true;
        });
    }

    // Description templates
    document.querySelectorAll('.template-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const template = e.target.getAttribute('data-template');
            insertTemplate(template);
        });
    });

    // Description counter
    const descriptionArea = document.getElementById('description');
    if (descriptionArea) {
        descriptionArea.addEventListener('input', updateDescriptionCounter);
    }

    // Tags
    const addTagBtn = document.getElementById('add-tag-btn');
    if (addTagBtn) {
        addTagBtn.addEventListener('click', addTag);
    }

    const tagInput = document.getElementById('tag-input');
    if (tagInput) {
        tagInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                e.preventDefault();
                addTag();
            }
        });
    }

    // Suggested tags
    document.querySelectorAll('.suggested-tag').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const tag = e.target.getAttribute('data-tag');
            addSuggestedTag(tag);
        });
    });

    // Publish schedule toggle
    document.querySelectorAll('input[name="publish-time"]').forEach(radio => {
        radio.addEventListener('change', toggleSchedule);
    });

    // Form submission
    const uploadForm = document.getElementById('uploadForm');
    if (uploadForm) {
        uploadForm.addEventListener('submit', (e) => {
            e.preventDefault();
            uploadToYouTube();
        });
    }
}

// ═══════════════════════════════════════════════════════════════
// VIDEO SELECTION
// ═══════════════════════════════════════════════════════════════

async function loadReadyVideos() {
    try {
        const response = await fetch('http://localhost:5001/api/videos');
        const videos = await response.json();

        const select = document.getElementById('video-select');
        select.innerHTML = '<option value="">Выберите видео для загрузки...</option>';

        if (videos && videos.length > 0) {
            videos.forEach(video => {
                const option = document.createElement('option');
                option.value = video.id;
                option.textContent = `${video.title} (${video.duration || 'N/A'})`;
                option.dataset.video = JSON.stringify(video);
                select.appendChild(option);
            });
        } else {
            select.innerHTML = '<option value="">Нет готовых видео</option>';
        }
    } catch (error) {
        console.error('Error loading videos:', error);
        const select = document.getElementById('video-select');
        select.innerHTML = '<option value="">Ошибка загрузки видео</option>';
    }
}

function selectVideo(videoId) {
    if (!videoId) {
        document.getElementById('video-preview').style.display = 'none';
        selectedVideo = null;
        return;
    }

    const select = document.getElementById('video-select');
    const option = select.options[select.selectedIndex];
    const video = JSON.parse(option.dataset.video || '{}');

    selectedVideo = video;

    // Show preview
    const preview = document.getElementById('video-preview');
    document.getElementById('preview-title').textContent = video.title || 'Без названия';
    document.getElementById('preview-meta').textContent = `Длительность: ${video.duration || 'N/A'} | Размер: ${video.size || 'N/A'}`;
    document.getElementById('preview-date').textContent = `Создано: ${video.created_at || 'N/A'}`;

    // Set thumbnail if available
    if (video.thumbnail) {
        document.getElementById('preview-thumb').src = video.thumbnail;
    }

    preview.style.display = 'block';

    // Auto-fill custom title if empty
    const customInput = document.getElementById('custom-title-input');
    if (customInput && !customInput.value && video.title) {
        customInput.value = video.title;
        updateCustomTitleCounter();
    }
}

// ═══════════════════════════════════════════════════════════════
// TITLE GENERATION
// ═══════════════════════════════════════════════════════════════

function generateTitleVariants() {
    const customInput = document.getElementById('custom-title-input');
    const baseTopic = customInput.value || selectedVideo?.title || 'Ваша Тема';

    // Clean topic (remove extra words)
    const cleanTopic = baseTopic.replace(/^(Как|Почему|Что|Когда)\s+/i, '').substring(0, 60);

    // Variant 1: Emotional
    const variant1 = `😱 ${cleanTopic}! Вы НЕ ПОВЕРИТЕ...`;
    document.getElementById('title-text-1').textContent = variant1;
    document.getElementById('title-length-1').textContent = `${variant1.length}/100`;

    // Variant 2: Numbered
    const variant2 = `7 Секретов ${cleanTopic} от Экспертов`;
    document.getElementById('title-text-2').textContent = variant2;
    document.getElementById('title-length-2').textContent = `${variant2.length}/100`;

    // Variant 3: Question
    const variant3 = `Почему ${cleanTopic} Меняет Всё?`;
    document.getElementById('title-text-3').textContent = variant3;
    document.getElementById('title-length-3').textContent = `${variant3.length}/100`;

    console.log('Generated title variants');
}

function selectTitleVariant(index) {
    const titleText = document.getElementById(`title-text-${index}`).textContent;
    const customInput = document.getElementById('custom-title-input');
    customInput.value = titleText;
    updateCustomTitleCounter();
}

function updateCustomTitleCounter() {
    const input = document.getElementById('custom-title-input');
    const counter = document.getElementById('custom-title-length');
    const length = input.value.length;
    counter.textContent = `${length}/100`;

    // Warning if too long
    if (length > 100) {
        counter.style.color = '#ff4444';
    } else if (length > 80) {
        counter.style.color = '#ffaa00';
    } else {
        counter.style.color = '#666';
    }
}

// ═══════════════════════════════════════════════════════════════
// DESCRIPTION TEMPLATES
// ═══════════════════════════════════════════════════════════════

function insertTemplate(type) {
    if (!templates[type]) {
        console.error('Unknown template:', type);
        return;
    }

    const textarea = document.getElementById('description');
    const topic = document.getElementById('custom-title-input').value || 'этой теме';

    // Replace [тему] placeholder
    let template = templates[type].replace('[тему]', topic.toLowerCase());
    template = template.replace('[теме]', topic.toLowerCase());

    textarea.value = template;
    updateDescriptionCounter();

    console.log(`Inserted ${type} template`);
}

function updateDescriptionCounter() {
    const textarea = document.getElementById('description');
    const counter = document.getElementById('description-counter');
    const length = textarea.value.length;
    counter.textContent = `${length}/5000`;

    if (length > 5000) {
        counter.style.color = '#ff4444';
    } else if (length > 4500) {
        counter.style.color = '#ffaa00';
    } else {
        counter.style.color = '#666';
    }
}

// ═══════════════════════════════════════════════════════════════
// TAGS MANAGEMENT
// ═══════════════════════════════════════════════════════════════

function addTag() {
    const input = document.getElementById('tag-input');
    const tag = input.value.trim().toLowerCase();

    if (!tag) return;

    // Check if already exists
    if (currentTags.includes(tag)) {
        alert('Этот тег уже добавлен');
        input.value = '';
        return;
    }

    // Check total length
    const totalLength = currentTags.join(',').length + tag.length;
    if (totalLength > 500) {
        alert('Превышен лимит символов для тегов (500)');
        return;
    }

    currentTags.push(tag);
    renderTags();
    input.value = '';
    updateTagsCounter();
}

function addSuggestedTag(tag) {
    if (currentTags.includes(tag)) {
        alert('Этот тег уже добавлен');
        return;
    }

    const totalLength = currentTags.join(',').length + tag.length;
    if (totalLength > 500) {
        alert('Превышен лимит символов для тегов (500)');
        return;
    }

    currentTags.push(tag);
    renderTags();
    updateTagsCounter();
}

function removeTag(tag) {
    currentTags = currentTags.filter(t => t !== tag);
    renderTags();
    updateTagsCounter();
}

function renderTags() {
    const container = document.getElementById('tags-container');
    container.innerHTML = '';

    currentTags.forEach(tag => {
        const chip = document.createElement('div');
        chip.className = 'tag-chip';
        chip.innerHTML = `
            <span>${tag}</span>
            <button class="remove-tag" onclick="removeTag('${tag}')">×</button>
        `;
        container.appendChild(chip);
    });

    if (currentTags.length === 0) {
        container.innerHTML = '<span style="color: #666; font-size: 12px;">Добавьте теги для улучшения поиска видео</span>';
    }
}

function updateTagsCounter() {
    const counter = document.getElementById('tags-counter');
    const totalLength = currentTags.join(',').length;
    counter.textContent = `${totalLength}/500`;

    if (totalLength > 500) {
        counter.style.color = '#ff4444';
    } else if (totalLength > 450) {
        counter.style.color = '#ffaa00';
    } else {
        counter.style.color = '#666';
    }
}

// ═══════════════════════════════════════════════════════════════
// SCHEDULE TOGGLE
// ═══════════════════════════════════════════════════════════════

function toggleSchedule() {
    const scheduleRadio = document.getElementById('publish-schedule');
    const schedulePicker = document.getElementById('schedule-picker');

    if (scheduleRadio && scheduleRadio.checked) {
        schedulePicker.style.display = 'block';

        // Set default date/time (tomorrow at 12:00)
        const tomorrow = new Date();
        tomorrow.setDate(tomorrow.getDate() + 1);

        const dateInput = document.getElementById('schedule-date');
        const timeInput = document.getElementById('schedule-time');

        if (dateInput && !dateInput.value) {
            dateInput.value = tomorrow.toISOString().split('T')[0];
        }

        if (timeInput && !timeInput.value) {
            timeInput.value = '12:00';
        }
    } else {
        schedulePicker.style.display = 'none';
    }
}

// ═══════════════════════════════════════════════════════════════
// DRAFT MANAGEMENT
// ═══════════════════════════════════════════════════════════════

function saveDraft() {
    const draft = {
        videoId: selectedVideo?.id,
        title: document.getElementById('custom-title-input').value,
        description: document.getElementById('description').value,
        tags: currentTags,
        category: document.getElementById('category').value,
        privacy: document.querySelector('input[name="privacy"]:checked')?.value,
        publishTime: document.querySelector('input[name="publish-time"]:checked')?.value,
        scheduleDate: document.getElementById('schedule-date')?.value,
        scheduleTime: document.getElementById('schedule-time')?.value,
        enableComments: document.getElementById('enable-comments')?.checked,
        enableRatings: document.getElementById('enable-ratings')?.checked,
        madeForKids: document.getElementById('made-for-kids')?.checked,
        ageRestriction: document.getElementById('age-restriction')?.checked,
        notifySubscribers: document.getElementById('notify-subscribers')?.checked,
        savedAt: new Date().toISOString()
    };

    localStorage.setItem('youtube-upload-draft', JSON.stringify(draft));
    alert('💾 Черновик сохранён!');
    console.log('Draft saved:', draft);
}

function loadDraft() {
    const draftJson = localStorage.getItem('youtube-upload-draft');
    if (!draftJson) return;

    try {
        const draft = JSON.parse(draftJson);

        // Ask user if they want to load draft
        const savedDate = new Date(draft.savedAt).toLocaleString('ru-RU');
        const loadDraft = confirm(`Найден сохранённый черновик от ${savedDate}.\n\nЗагрузить его?`);

        if (!loadDraft) {
            localStorage.removeItem('youtube-upload-draft');
            return;
        }

        // Load draft data
        if (draft.videoId) {
            const videoSelect = document.getElementById('video-select');
            videoSelect.value = draft.videoId;
            selectVideo(draft.videoId);
        }

        if (draft.title) {
            document.getElementById('custom-title-input').value = draft.title;
            updateCustomTitleCounter();
        }

        if (draft.description) {
            document.getElementById('description').value = draft.description;
            updateDescriptionCounter();
        }

        if (draft.tags && draft.tags.length > 0) {
            currentTags = draft.tags;
            renderTags();
            updateTagsCounter();
        }

        if (draft.category) {
            document.getElementById('category').value = draft.category;
        }

        if (draft.privacy) {
            document.getElementById(`privacy-${draft.privacy}`).checked = true;
        }

        if (draft.publishTime) {
            document.getElementById(`publish-${draft.publishTime}`).checked = true;
            toggleSchedule();
        }

        if (draft.scheduleDate) {
            document.getElementById('schedule-date').value = draft.scheduleDate;
        }

        if (draft.scheduleTime) {
            document.getElementById('schedule-time').value = draft.scheduleTime;
        }

        // Checkboxes
        if (draft.enableComments !== undefined) {
            document.getElementById('enable-comments').checked = draft.enableComments;
        }

        if (draft.enableRatings !== undefined) {
            document.getElementById('enable-ratings').checked = draft.enableRatings;
        }

        if (draft.madeForKids !== undefined) {
            document.getElementById('made-for-kids').checked = draft.madeForKids;
        }

        if (draft.ageRestriction !== undefined) {
            document.getElementById('age-restriction').checked = draft.ageRestriction;
        }

        if (draft.notifySubscribers !== undefined) {
            document.getElementById('notify-subscribers').checked = draft.notifySubscribers;
        }

        console.log('Draft loaded:', draft);
    } catch (error) {
        console.error('Error loading draft:', error);
        localStorage.removeItem('youtube-upload-draft');
    }
}

// ═══════════════════════════════════════════════════════════════
// UPLOAD TO YOUTUBE
// ═══════════════════════════════════════════════════════════════

function uploadToYouTube() {
    // Validation
    if (!selectedVideo) {
        alert('⚠️ Выберите видео для загрузки');
        return;
    }

    const title = document.getElementById('custom-title-input').value;
    if (!title || title.trim().length === 0) {
        alert('⚠️ Введите название видео');
        return;
    }

    const description = document.getElementById('description').value;
    const category = document.getElementById('category').value;
    const privacy = document.querySelector('input[name="privacy"]:checked')?.value;

    if (!category) {
        alert('⚠️ Выберите категорию видео');
        return;
    }

    // Show PHASE 2 alert
    alert(`📤 Функция загрузки на YouTube будет доступна в ФАЗЕ 2

После добавления YouTube API вы сможете:

✅ Загружать видео напрямую на канал
✅ Редактировать метаданные
✅ Планировать публикации
✅ Отслеживать статус загрузки

Ваши данные:
━━━━━━━━━━━━━━━━
📝 Название: ${title}
📂 Категория: ${document.getElementById('category').options[document.getElementById('category').selectedIndex].text}
🔒 Приватность: ${privacy}
🏷️ Теги: ${currentTags.length} шт.
📄 Описание: ${description.length} символов

Нажмите OK для возврата.`);

    console.log('Upload data:', {
        video: selectedVideo,
        title,
        description,
        tags: currentTags,
        category,
        privacy,
        publishTime: document.querySelector('input[name="publish-time"]:checked')?.value,
        scheduleDate: document.getElementById('schedule-date')?.value,
        scheduleTime: document.getElementById('schedule-time')?.value
    });
}

// ═══════════════════════════════════════════════════════════════
// NAVIGATION
// ═══════════════════════════════════════════════════════════════

function goBack() {
    // Ask if want to save draft
    const hasData = document.getElementById('custom-title-input').value ||
                    document.getElementById('description').value ||
                    currentTags.length > 0;

    if (hasData) {
        const save = confirm('Хотите сохранить черновик перед выходом?');
        if (save) {
            saveDraft();
        }
    }

    window.location.href = 'index.html';
}

// ═══════════════════════════════════════════════════════════════
// EXPOSE FUNCTIONS TO GLOBAL SCOPE
// ═══════════════════════════════════════════════════════════════

window.goBack = goBack;
window.saveDraft = saveDraft;
window.removeTag = removeTag;

console.log('✅ YouTube Upload JS loaded');
