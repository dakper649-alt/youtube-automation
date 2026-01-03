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
  alert('⚙️ Настройки\n\nДля настройки API ключей отредактируйте файл .env в корневой директории проекта.');
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
});
