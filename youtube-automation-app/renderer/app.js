// UI State
let isGenerating = false;

// Image Styles Configuration (20 professional styles)
const IMAGE_STYLES = {
    'minimalist_stick_figure': { name: '👤 Minimalist Stick Figure', desc: 'Простые фигуры - психология' },
    'anime': { name: '🎨 Anime Style', desc: 'Яркий аниме - истории' },
    'watercolor': { name: '🖌️ Watercolor Painting', desc: 'Акварель - wellness' },
    'oil_painting': { name: '🖼️ Oil Painting', desc: 'Классика - серьёзный контент' },
    'cyberpunk': { name: '🌃 Cyberpunk', desc: 'Неон - технологии' },
    'retro_80s': { name: '📼 Retro 80s', desc: 'Ретро - ностальгия' },
    'pixel_art': { name: '🎮 Pixel Art', desc: 'Пиксели - геймеры' },
    'comic_book': { name: '💥 Comic Book', desc: 'Комиксы - экшен' },
    'photorealistic': { name: '📷 Photorealistic', desc: 'Фото - документальное' },
    'clay_animation': { name: '🧸 Clay Animation', desc: 'Пластилин - дети' },
    'paper_cutout': { name: '✂️ Paper Cut-out', desc: 'Аппликация - творчество' },
    'neon_glow': { name: '✨ Neon Glow', desc: 'Неон - ночь' },
    'abstract_art': { name: '🎭 Abstract Art', desc: 'Абстракция - философия' },
    'low_poly_3d': { name: '🔷 Low Poly 3D', desc: '3D графика - дизайн' },
    'sketch_drawing': { name: '✏️ Sketch Drawing', desc: 'Набросок - искусство' },
    'digital_art': { name: '💻 Digital Art', desc: 'Цифровое - универсально' },
    'fantasy_art': { name: '🧙 Fantasy Art', desc: 'Фэнтези - магия' },
    'scifi_concept': { name: '🚀 Sci-Fi Concept', desc: 'Sci-Fi - будущее' },
    'vintage_poster': { name: '📜 Vintage Poster', desc: 'Винтаж - ретро' },
    'flat_design': { name: '📊 Flat Design', desc: 'Плоский - бизнес' }
};

// Voice Configuration (15 ElevenLabs voices)
const VOICES = {
    // Психология / Wellness
    'rachel': { name: '🎭 Rachel', desc: 'Теплый, дружелюбный (Psychology)', tag: '⭐ Лучший для психологии', recommended: true },
    'charlotte': { name: '👩‍🏫 Charlotte', desc: 'Профессиональный (Education)' },
    'grace': { name: '🧘‍♀️ Grace', desc: 'Спокойный, мудрый (Meditation)' },

    // Бизнес / Мотивация
    'adam': { name: '💼 Adam', desc: 'Уверенный, авторитетный (Business)', tag: '⭐ Лучший для бизнеса', recommended: true },
    'antoni': { name: '🚀 Antoni', desc: 'Энергичный (Entrepreneurship)' },
    'josh': { name: '⭐ Josh', desc: 'Позитивный, вдохновляющий (Motivation)' },
    'arnold': { name: '🎙️ Arnold', desc: 'Глубокий, спокойный (Finance)' },

    // Истории / Развлечения
    'bella': { name: '🎬 Bella', desc: 'Эмоциональный, драматичный (Stories)', tag: '⭐ Лучший для историй', recommended: true },
    'elli': { name: '🎉 Elli', desc: 'Молодой, игривый (Entertainment)' },
    'sam': { name: '🎭 Sam', desc: 'Динамичный, захватывающий (Thriller)' },

    // Образование / Наука
    'domi': { name: '📚 Domi', desc: 'Ясный, образовательный (Tutorial)' },
    'ethan': { name: '🔬 Ethan', desc: 'Умный, информативный (Science)' },

    // Дополнительные
    'callum': { name: '📰 Callum', desc: 'Спокойный, надёжный (Documentary)' },
    'daniel': { name: '🎩 Daniel', desc: 'Британский, благородный (History)' },
    'lily': { name: '🌸 Lily', desc: 'Элегантный, утончённый (Culture)' }
};

// Background Music Configuration (13 tracks)
const BACKGROUND_MUSIC = {
    // Психология / Wellness
    'calm_piano': { name: '🎹 Calm Piano', desc: 'Спокойное фортепиано - психология', tag: '⭐ Рекомендовано', recommended: true },
    'soft_strings': { name: '🎻 Soft Strings', desc: 'Мягкие струнные - медитация' },
    'ambient_nature': { name: '🌿 Ambient Nature', desc: 'Звуки природы - релакс' },

    // Бизнес / Мотивация
    'uplifting_corporate': { name: '💼 Uplifting Corporate', desc: 'Мотивирующая - бизнес', tag: '⭐ Рекомендовано', recommended: true },
    'inspiring_orchestral': { name: '🎺 Inspiring Orchestral', desc: 'Вдохновляющая - успех' },
    'modern_tech': { name: '💻 Modern Tech', desc: 'Современная - технологии' },

    // Истории / Драма
    'cinematic_tension': { name: '🎬 Cinematic Tension', desc: 'Напряжение - триллер', tag: '⭐ Рекомендовано', recommended: true },
    'emotional_piano': { name: '😢 Emotional Piano', desc: 'Эмоциональная - драма' },
    'suspense_strings': { name: '🔍 Suspense Strings', desc: 'Саспенс - детектив' },

    // Образование
    'light_background': { name: '📚 Light Background', desc: 'Лёгкая - обучение', tag: '⭐ Рекомендовано', recommended: true },
    'neutral_corporate': { name: '📊 Neutral Corporate', desc: 'Нейтральная - презентации' },

    // Энергичное
    'upbeat_acoustic': { name: '🎸 Upbeat Acoustic', desc: 'Позитивная - лайфстайл' },
    'energetic_pop': { name: '🎉 Energetic Pop', desc: 'Энергичная - развлечения' },

    // Без музыки
    'no_music': { name: '🔇 No Music', desc: 'Без фоновой музыки' }
};

// Initialize UI on load
function initializeUI() {
    // Populate style dropdown
    const styleSelect = document.getElementById('style');
    styleSelect.innerHTML = '';

    for (const [key, data] of Object.entries(IMAGE_STYLES)) {
        const option = document.createElement('option');
        option.value = key;
        option.textContent = `${data.name} - ${data.desc}`;
        styleSelect.appendChild(option);
    }

    // Set default style
    styleSelect.value = 'minimalist_stick_figure';

    console.log('✅ UI initialized with 20 image styles');

    // Populate voice dropdown
    const voiceSelect = document.getElementById('voice');
    voiceSelect.innerHTML = '';

    for (const [key, data] of Object.entries(VOICES)) {
        const option = document.createElement('option');
        option.value = key;
        const tag = data.tag ? ` ${data.tag}` : '';
        option.textContent = `${data.name} - ${data.desc}${tag}`;
        voiceSelect.appendChild(option);
    }

    // Set default voice
    voiceSelect.value = 'rachel';

    // Add preview button if not exists
    const voiceGroup = voiceSelect.parentElement;
    if (!document.getElementById('previewVoiceBtn')) {
        const previewButton = document.createElement('button');
        previewButton.id = 'previewVoiceBtn';
        previewButton.type = 'button';
        previewButton.className = 'preview-voice-btn';
        previewButton.innerHTML = '▶️ Прослушать';
        previewButton.onclick = playVoicePreview;
        voiceGroup.appendChild(previewButton);
    }

    console.log('✅ UI initialized with 15 ElevenLabs voices');

    // Populate music dropdown
    const musicSelect = document.getElementById('music');
    if (musicSelect) {
        musicSelect.innerHTML = '';

        for (const [key, data] of Object.entries(BACKGROUND_MUSIC)) {
            const option = document.createElement('option');
            option.value = key;
            const tag = data.tag ? ` ${data.tag}` : '';
            option.textContent = `${data.name} - ${data.desc}${tag}`;
            musicSelect.appendChild(option);
        }

        // Set default music
        musicSelect.value = 'calm_piano';

        console.log('✅ UI initialized with 13 background music tracks');
    }
}

async function playVoicePreview() {
    const voiceSelect = document.getElementById('voice');
    const selectedVoice = voiceSelect.value;
    const previewButton = document.getElementById('previewVoiceBtn');

    try {
        previewButton.innerHTML = '⏳ Загрузка...';
        previewButton.disabled = true;

        // Fetch audio from API
        const response = await fetch(`http://localhost:5001/api/preview-voice/${selectedVoice}`);

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Failed to generate preview');
        }

        // Create audio from blob
        const blob = await response.blob();
        const audioUrl = URL.createObjectURL(blob);
        const audio = new Audio(audioUrl);

        previewButton.innerHTML = '⏸️ Играет...';

        audio.onended = () => {
            previewButton.innerHTML = '▶️ Прослушать';
            previewButton.disabled = false;
            URL.revokeObjectURL(audioUrl);
        };

        audio.onerror = () => {
            previewButton.innerHTML = '▶️ Прослушать';
            previewButton.disabled = false;
            URL.revokeObjectURL(audioUrl);
            alert('Ошибка воспроизведения аудио');
        };

        await audio.play();

    } catch (error) {
        console.error('Voice preview error:', error);
        alert('Ошибка прослушки голоса: ' + error.message);
        previewButton.innerHTML = '▶️ Прослушать';
        previewButton.disabled = false;
    }
}

// Form submission
document.getElementById('createVideoForm').addEventListener('submit', async (e) => {
  e.preventDefault();

  if (isGenerating) return;

  const formData = {
    topic: document.getElementById('topic').value,
    niche: document.getElementById('niche').value,
    style: document.getElementById('style').value,
    voice: document.getElementById('voice').value,
    music: document.getElementById('music')?.value || 'no_music',
    length: parseInt(document.getElementById('length').value)
  };

  startVideoGeneration(formData);
});

async function startVideoGeneration(data) {
  isGenerating = true;

  // Disable submit button
  const submitBtn = document.querySelector('.btn-primary');
  submitBtn.disabled = true;
  submitBtn.textContent = '⏳ Генерация...';

  // Show progress section
  document.getElementById('progressSection').style.display = 'block';
  document.getElementById('progressSection').scrollIntoView({ behavior: 'smooth' });

  try {
    // Call Flask API через fetch
    const response = await fetch('http://localhost:5001/api/create-video', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(data)
    });

    const result = await response.json();

    if (result.success) {
      // Start polling for progress
      pollProgress(result.task_id);
    } else {
      throw new Error(result.error || 'Unknown error');
    }
  } catch (error) {
    console.error('Error:', error);
    alert('Ошибка подключения к серверу: ' + error.message + '\n\nУбедитесь что Flask сервер запущен.');
    resetUI();
  }
}

function pollProgress(taskId) {
  const interval = setInterval(async () => {
    try {
      const response = await fetch(`http://localhost:5001/api/progress/${taskId}`);
      const data = await response.json();

      updateProgress(data);

      if (data.status === 'completed') {
        clearInterval(interval);
        onVideoComplete(data);
      } else if (data.status === 'error') {
        clearInterval(interval);
        onVideoError(data);
      }
    } catch (error) {
      console.error('Progress poll error:', error);
    }
  }, 2000); // Poll every 2 seconds
}

function updateProgress(data) {
  document.getElementById('currentStep').textContent = data.step || 'Генерация...';
  document.getElementById('progressBar').style.width = (data.progress || 0) + '%';
  document.getElementById('progressPercent').textContent = (data.progress || 0) + '%';
  document.getElementById('timeRemaining').textContent = `Осталось: ~${data.timeRemaining || 60} минут`;
}

function onVideoComplete(data) {
  resetUI();

  // Add video to list
  if (data.video) {
    addVideoToList(data.video);
  }

  // Show notification
  alert('🎉 Видео готово!\n\n' + (data.video?.title || 'Видео успешно создано!'));
}

function onVideoError(data) {
  resetUI();
  alert('❌ Ошибка генерации:\n\n' + (data.error || 'Неизвестная ошибка'));
}

function resetUI() {
  isGenerating = false;

  const submitBtn = document.querySelector('.btn-primary');
  submitBtn.disabled = false;
  submitBtn.textContent = '🚀 Создать видео';

  document.getElementById('progressSection').style.display = 'none';
}

function addVideoToList(video) {
  const videosList = document.getElementById('videosList');

  // Remove empty state
  const emptyState = videosList.querySelector('.empty-state');
  if (emptyState) {
    emptyState.remove();
  }

  // Add video card
  const videoCard = document.createElement('div');
  videoCard.className = 'video-card';
  videoCard.innerHTML = `
    <h3>${video.title || 'Новое видео'}</h3>
    <p>Длительность: ${video.duration || 'N/A'}</p>
    <p>Создано: ${new Date().toLocaleString('ru-RU')}</p>
    <button onclick="openVideo('${video.path}')">▶️ Открыть</button>
  `;

  videosList.prepend(videoCard);
}

function openVideo(path) {
  // Open video in default app
  fetch('http://localhost:5001/api/open-file', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ path })
  });
}

function openSettings() {
  window.location.href = 'settings.html';
}

function openStats() {
  window.location.href = 'stats.html';
}

// Backend ready listener
if (window.electronAPI) {
  window.electronAPI.onBackendReady(() => {
    console.log('✅ Backend server is ready!');
  });
}

// Check if backend is ready on load
window.addEventListener('load', async () => {
  // Initialize UI with 20 styles
  initializeUI();

  // Check backend health
  try {
    const response = await fetch('http://localhost:5001/api/health');
    if (response.ok) {
      console.log('✅ Flask server is running');
    }
  } catch (error) {
    console.warn('⚠️ Flask server not ready yet:', error.message);
  }

  // Load videos
  await loadVideos();
});

// ═══════════════════════════════════════════════════════════════
// VIDEO LIBRARY
// ═══════════════════════════════════════════════════════════════

let currentPage = 1;
const videosPerPage = 12;
let allVideos = [];
let filteredVideos = [];

async function loadVideos() {
  try {
    const response = await fetch('http://localhost:5001/api/videos');
    if (!response.ok) throw new Error('Failed to load videos');

    allVideos = await response.json();
    filteredVideos = allVideos;

    console.log(`📊 Loaded ${allVideos.length} videos`);
    applyFilters();
    renderVideos();
  } catch (error) {
    console.error('Error loading videos:', error);
    showEmptyState();
  }
}

function applyFilters() {
  const searchQuery = document.getElementById('search-videos')?.value.toLowerCase() || '';
  const statusFilter = document.getElementById('filter-status')?.value || 'all';
  const nicheFilter = document.getElementById('filter-niche')?.value || 'all';

  filteredVideos = allVideos.filter(video => {
    const matchesSearch = video.topic.toLowerCase().includes(searchQuery);
    const matchesStatus = statusFilter === 'all' || video.status === statusFilter;
    const matchesNiche = nicheFilter === 'all' || video.niche === nicheFilter;

    return matchesSearch && matchesStatus && matchesNiche;
  });

  currentPage = 1;
  renderVideos();
}

function renderVideos() {
  const videosList = document.getElementById('videos-list');

  if (!filteredVideos || filteredVideos.length === 0) {
    showEmptyState();
    return;
  }

  // Pagination
  const startIndex = (currentPage - 1) * videosPerPage;
  const endIndex = startIndex + videosPerPage;
  const videosToShow = filteredVideos.slice(startIndex, endIndex);

  // Render cards
  videosList.innerHTML = videosToShow.map(video => `
    <div class="video-card" onclick="openVideo('${video.id}')">
      <div class="video-thumbnail">
        ${video.thumbnail
          ? `<img src="${video.thumbnail}" alt="${video.topic}">`
          : `<div class="play-icon">▶️</div>`
        }
        <span class="video-status ${video.status}">${getStatusText(video.status)}</span>
        <span class="video-duration">${formatDuration(video.duration_seconds || 0)}</span>
      </div>

      <div class="video-info">
        <h3 class="video-title">${escapeHtml(video.topic)}</h3>

        <div class="video-meta">
          <span>📅 ${formatDate(video.created_at)}</span>
          <span>🎨 ${video.style || 'N/A'}</span>
          <span>🎙️ ${video.voice || 'N/A'}</span>
        </div>

        <div class="video-tags">
          <span class="video-tag">${video.niche || 'general'}</span>
          ${video.music && video.music !== 'no_music' ? `<span class="video-tag">🎵 ${video.music}</span>` : ''}
        </div>

        <div class="video-actions" onclick="event.stopPropagation()">
          <button class="video-action-btn primary" onclick="playVideo('${escapeHtml(video.video_path || '')}')">
            ▶️ Смотреть
          </button>
          <button class="video-action-btn" onclick="openVideoFolder('${escapeHtml(video.video_path || '')}')">
            📂 Папка
          </button>
          <button class="video-action-btn" onclick="uploadToYouTube('${video.id}')">
            📤 YouTube
          </button>
          <button class="video-action-btn danger" onclick="deleteVideo(${video.id})">
            🗑️
          </button>
        </div>
      </div>
    </div>
  `).join('');

  updatePagination();
}

function showEmptyState() {
  const videosList = document.getElementById('videos-list');
  if (!videosList) return;

  videosList.innerHTML = `
    <div class="empty-state">
      <div class="empty-state-icon">🎬</div>
      <div class="empty-state-text">Видео ещё не созданы</div>
      <div class="empty-state-hint">Создайте первое видео, чтобы оно появилось здесь</div>
    </div>
  `;
}

function updatePagination() {
  const totalPages = Math.ceil(filteredVideos.length / videosPerPage);

  const pageInfo = document.getElementById('page-info');
  const prevBtn = document.getElementById('prev-page');
  const nextBtn = document.getElementById('next-page');

  if (pageInfo) pageInfo.textContent = `Страница ${currentPage} из ${totalPages || 1}`;
  if (prevBtn) prevBtn.disabled = currentPage === 1;
  if (nextBtn) nextBtn.disabled = currentPage === totalPages || totalPages === 0;
}

// Utilities
function getStatusText(status) {
  const statuses = {
    'completed': '✅ Готово',
    'processing': '⏳ В процессе',
    'error': '❌ Ошибка'
  };
  return statuses[status] || status;
}

function formatDuration(seconds) {
  if (!seconds) return '0:00';
  const mins = Math.floor(seconds / 60);
  const secs = seconds % 60;
  return `${mins}:${secs.toString().padStart(2, '0')}`;
}

function formatDate(dateString) {
  if (!dateString) return 'N/A';
  const date = new Date(dateString);
  return date.toLocaleDateString('ru-RU', { day: 'numeric', month: 'short', year: 'numeric' });
}

function escapeHtml(text) {
  if (!text) return '';
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}

// Video Actions
function openVideo(videoId) {
  console.log('Opening video:', videoId);
  // TODO: Modal with details
  alert(`Видео ID: ${videoId}\nДетали видео (скоро)`);
}

async function playVideo(videoPath) {
  if (!videoPath) {
    alert('Путь к видео не найден');
    return;
  }

  try {
    await fetch('http://localhost:5001/api/open-file', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ path: videoPath })
    });
    console.log('✅ Video opened:', videoPath);
  } catch (error) {
    console.error('Error opening video:', error);
    alert('Ошибка открытия видео');
  }
}

async function openVideoFolder(videoPath) {
  if (!videoPath) {
    alert('Путь к видео не найден');
    return;
  }

  try {
    // Extract folder path
    const folderPath = videoPath.substring(0, videoPath.lastIndexOf('/'));

    await fetch('http://localhost:5001/api/open-file', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ path: folderPath })
    });
    console.log('✅ Folder opened:', folderPath);
  } catch (error) {
    console.error('Error opening folder:', error);
    alert('Ошибка открытия папки');
  }
}

async function uploadToYouTube(videoId) {
  // TODO: YouTube upload (PHASE 2)
  alert('📤 Функция автопостинга на YouTube будет добавлена в ФАЗЕ 2');
}

async function deleteVideo(videoId) {
  if (!confirm('Вы уверены, что хотите удалить это видео?')) return;

  try {
    const response = await fetch(`http://localhost:5001/api/videos/${videoId}`, {
      method: 'DELETE'
    });

    if (!response.ok) throw new Error('Failed to delete');

    console.log('✅ Video deleted:', videoId);
    await loadVideos(); // Reload list
  } catch (error) {
    console.error('Error deleting video:', error);
    alert('Ошибка удаления видео');
  }
}

// Event Listeners
document.getElementById('search-videos')?.addEventListener('input', applyFilters);
document.getElementById('filter-status')?.addEventListener('change', applyFilters);
document.getElementById('filter-niche')?.addEventListener('change', applyFilters);
document.getElementById('refresh-videos')?.addEventListener('click', loadVideos);

document.getElementById('prev-page')?.addEventListener('click', () => {
  if (currentPage > 1) {
    currentPage--;
    renderVideos();
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }
});

document.getElementById('next-page')?.addEventListener('click', () => {
  const totalPages = Math.ceil(filteredVideos.length / videosPerPage);
  if (currentPage < totalPages) {
    currentPage++;
    renderVideos();
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }
});

// Auto-refresh every 30 seconds
setInterval(loadVideos, 30000);
