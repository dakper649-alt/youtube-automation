// UI State
let isGenerating = false;

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
  try {
    const response = await fetch('http://localhost:5001/api/health');
    if (response.ok) {
      console.log('✅ Flask server is running');
    }
  } catch (error) {
    console.warn('⚠️ Flask server not ready yet:', error.message);
  }
});
