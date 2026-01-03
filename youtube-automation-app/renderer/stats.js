// ═══════════════════════════════════════════════════════════════
// STATS DASHBOARD LOGIC
// ═══════════════════════════════════════════════════════════════

// Chart instances
let videosByDayChart = null;
let stylesChart = null;
let voicesChart = null;
let timeOfDayChart = null;

// Stats data
let statsData = null;

// ═══════════════════════════════════════════════════════════════
// INITIALIZATION
// ═══════════════════════════════════════════════════════════════

document.addEventListener('DOMContentLoaded', async () => {
    console.log('📊 Stats dashboard initialized');

    // Setup event listeners
    setupEventListeners();

    // Load stats data
    await loadStats();
});

// ═══════════════════════════════════════════════════════════════
// EVENT LISTENERS
// ═══════════════════════════════════════════════════════════════

function setupEventListeners() {
    // Back button
    document.getElementById('back-btn').addEventListener('click', () => {
        window.location.href = 'index.html';
    });

    // Refresh button
    document.getElementById('refresh-btn').addEventListener('click', async () => {
        await loadStats();
    });

    // Export buttons
    document.getElementById('export-csv-btn').addEventListener('click', exportToCSV);
    document.getElementById('export-json-btn').addEventListener('click', exportToJSON);
    document.getElementById('export-excel-btn').addEventListener('click', exportToExcel);

    // Edit goal buttons
    document.querySelectorAll('.edit-goal-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const goalType = e.target.closest('.goal-card').querySelector('.goal-header span').textContent.includes('Недельная') ? 'weekly' : 'monthly';
            editGoal(goalType);
        });
    });
}

// ═══════════════════════════════════════════════════════════════
// LOAD STATS DATA
// ═══════════════════════════════════════════════════════════════

async function loadStats() {
    try {
        const response = await fetch('http://localhost:5001/api/stats');

        if (!response.ok) {
            throw new Error('Failed to load stats');
        }

        statsData = await response.json();

        console.log('✅ Stats loaded:', statsData);

        // Update UI
        updateStatsCards(statsData);
        updateCharts(statsData);
        updateAPIUsage(statsData);
        updateAchievements(statsData);
        updateGoals(statsData);

    } catch (error) {
        console.error('❌ Error loading stats:', error);

        // Show demo data for development
        loadDemoData();
    }
}

function loadDemoData() {
    console.log('📊 Loading demo data...');

    statsData = {
        overview: {
            totalVideos: 42,
            totalTimeMinutes: 320,
            successRate: 95.2,
            avgDurationSeconds: 185
        },
        videosByDay: [
            { date: '2024-01-01', count: 3 },
            { date: '2024-01-02', count: 5 },
            { date: '2024-01-03', count: 2 },
            { date: '2024-01-04', count: 7 },
            { date: '2024-01-05', count: 4 },
            { date: '2024-01-06', count: 6 },
            { date: '2024-01-07', count: 8 }
        ],
        styleUsage: {
            'minimalist_stick_figure': 15,
            'vintage_cartoon': 10,
            'modern_flat': 8,
            'watercolor_sketch': 5,
            'bold_comic': 4
        },
        voiceUsage: {
            'rachel': 12,
            'adam': 10,
            'bella': 8,
            'josh': 7,
            'emily': 5
        },
        timeOfDay: {
            'morning': 8,
            'afternoon': 18,
            'evening': 12,
            'night': 4
        },
        apiUsage: {
            huggingface: { used: 245, limit: null },
            elevenlabs: { used: 1523, limit: 10000 },
            youtube: { used: 87, limit: 10000 },
            groq: { used: 312, limit: 14400 }
        },
        achievements: {
            first_video: true,
            ten_videos: true,
            hundred_videos: false,
            three_per_day: true,
            ten_per_week: false,
            thirty_day_streak: false
        },
        goals: {
            weekly: { current: 3, target: 10 },
            monthly: { current: 15, target: 40 }
        }
    };

    updateStatsCards(statsData);
    updateCharts(statsData);
    updateAPIUsage(statsData);
    updateAchievements(statsData);
    updateGoals(statsData);
}

// ═══════════════════════════════════════════════════════════════
// UPDATE STATS CARDS
// ═══════════════════════════════════════════════════════════════

function updateStatsCards(data) {
    const { overview } = data;

    // Total videos
    document.getElementById('total-videos').textContent = overview.totalVideos || 0;

    // Total time
    const hours = Math.floor(overview.totalTimeMinutes / 60);
    const minutes = overview.totalTimeMinutes % 60;
    document.getElementById('total-time').textContent = `${hours}ч ${minutes}м`;

    // Success rate
    document.getElementById('success-rate').textContent = `${overview.successRate.toFixed(1)}%`;

    // Average duration
    const avgMinutes = Math.floor(overview.avgDurationSeconds / 60);
    const avgSeconds = overview.avgDurationSeconds % 60;
    document.getElementById('avg-duration').textContent = `${avgMinutes}:${avgSeconds.toString().padStart(2, '0')}`;
}

// ═══════════════════════════════════════════════════════════════
// UPDATE CHARTS
// ═══════════════════════════════════════════════════════════════

function updateCharts(data) {
    updateVideosByDayChart(data.videosByDay);
    updateStylesChart(data.styleUsage);
    updateVoicesChart(data.voiceUsage);
    updateTimeOfDayChart(data.timeOfDay);
}

function updateVideosByDayChart(videosByDay) {
    const ctx = document.getElementById('videos-by-day-chart').getContext('2d');

    if (videosByDayChart) {
        videosByDayChart.destroy();
    }

    const labels = videosByDay.map(d => {
        const date = new Date(d.date);
        return date.toLocaleDateString('ru-RU', { month: 'short', day: 'numeric' });
    });
    const values = videosByDay.map(d => d.count);

    videosByDayChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'Видео',
                data: values,
                borderColor: '#667eea',
                backgroundColor: 'rgba(102, 126, 234, 0.1)',
                tension: 0.4,
                fill: true
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        color: '#888',
                        stepSize: 1
                    },
                    grid: {
                        color: '#2a2a2a'
                    }
                },
                x: {
                    ticks: {
                        color: '#888'
                    },
                    grid: {
                        color: '#2a2a2a'
                    }
                }
            }
        }
    });
}

function updateStylesChart(styleUsage) {
    const ctx = document.getElementById('styles-chart').getContext('2d');

    if (stylesChart) {
        stylesChart.destroy();
    }

    const labels = Object.keys(styleUsage).map(key => {
        return key.split('_').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ');
    });
    const values = Object.values(styleUsage);

    stylesChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [{
                data: values,
                backgroundColor: [
                    '#667eea',
                    '#764ba2',
                    '#f093fb',
                    '#4facfe',
                    '#00f2fe'
                ]
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        color: '#888',
                        padding: 15
                    }
                }
            }
        }
    });
}

function updateVoicesChart(voiceUsage) {
    const ctx = document.getElementById('voices-chart').getContext('2d');

    if (voicesChart) {
        voicesChart.destroy();
    }

    const labels = Object.keys(voiceUsage).map(key => {
        return key.charAt(0).toUpperCase() + key.slice(1);
    });
    const values = Object.values(voiceUsage);

    voicesChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Использований',
                data: values,
                backgroundColor: '#667eea'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        color: '#888',
                        stepSize: 1
                    },
                    grid: {
                        color: '#2a2a2a'
                    }
                },
                x: {
                    ticks: {
                        color: '#888'
                    },
                    grid: {
                        color: '#2a2a2a'
                    }
                }
            }
        }
    });
}

function updateTimeOfDayChart(timeOfDay) {
    const ctx = document.getElementById('time-of-day-chart').getContext('2d');

    if (timeOfDayChart) {
        timeOfDayChart.destroy();
    }

    const timeLabels = {
        morning: '🌅 Утро',
        afternoon: '☀️ День',
        evening: '🌆 Вечер',
        night: '🌙 Ночь'
    };

    const labels = Object.keys(timeOfDay).map(key => timeLabels[key]);
    const values = Object.values(timeOfDay);

    timeOfDayChart = new Chart(ctx, {
        type: 'polarArea',
        data: {
            labels: labels,
            datasets: [{
                data: values,
                backgroundColor: [
                    'rgba(255, 193, 7, 0.5)',
                    'rgba(102, 126, 234, 0.5)',
                    'rgba(239, 68, 68, 0.5)',
                    'rgba(59, 130, 246, 0.5)'
                ],
                borderColor: [
                    '#ffc107',
                    '#667eea',
                    '#ef4444',
                    '#3b82f6'
                ],
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        color: '#888',
                        padding: 15
                    }
                }
            },
            scales: {
                r: {
                    ticks: {
                        color: '#888',
                        backdropColor: 'transparent'
                    },
                    grid: {
                        color: '#2a2a2a'
                    }
                }
            }
        }
    });
}

// ═══════════════════════════════════════════════════════════════
// UPDATE API USAGE
// ═══════════════════════════════════════════════════════════════

function updateAPIUsage(data) {
    const { apiUsage } = data;

    // Hugging Face
    const hfUsed = apiUsage.huggingface.used;
    const hfLimit = apiUsage.huggingface.limit;
    document.getElementById('hf-text').textContent = `${hfUsed} / ${hfLimit ? hfLimit.toLocaleString() : '∞'}`;
    document.getElementById('hf-progress').style.width = hfLimit ? `${(hfUsed / hfLimit) * 100}%` : '0%';

    // ElevenLabs
    const elevenUsed = apiUsage.elevenlabs.used;
    const elevenLimit = apiUsage.elevenlabs.limit;
    const elevenPercent = (elevenUsed / elevenLimit) * 100;
    document.getElementById('elevenlabs-text').textContent = `${elevenUsed.toLocaleString()} / ${elevenLimit.toLocaleString()}`;
    document.getElementById('elevenlabs-progress').style.width = `${elevenPercent}%`;

    // YouTube
    const ytUsed = apiUsage.youtube.used;
    const ytLimit = apiUsage.youtube.limit;
    const ytPercent = (ytUsed / ytLimit) * 100;
    document.getElementById('youtube-text').textContent = `${ytUsed.toLocaleString()} / ${ytLimit.toLocaleString()}`;
    document.getElementById('youtube-progress').style.width = `${ytPercent}%`;

    // Groq
    const groqUsed = apiUsage.groq.used;
    const groqLimit = apiUsage.groq.limit;
    const groqPercent = (groqUsed / groqLimit) * 100;
    document.getElementById('groq-text').textContent = `${groqUsed.toLocaleString()} / ${groqLimit.toLocaleString()}`;
    document.getElementById('groq-progress').style.width = `${groqPercent}%`;
}

// ═══════════════════════════════════════════════════════════════
// UPDATE ACHIEVEMENTS
// ═══════════════════════════════════════════════════════════════

function updateAchievements(data) {
    const { achievements } = data;

    const achievementElements = document.querySelectorAll('.achievement');

    // Map achievement keys to element indices
    const achievementMap = [
        'first_video',
        'ten_videos',
        'hundred_videos',
        'three_per_day',
        'ten_per_week',
        'thirty_day_streak'
    ];

    achievementElements.forEach((element, index) => {
        const key = achievementMap[index];
        if (achievements[key]) {
            element.classList.remove('locked');
            element.classList.add('unlocked');
        } else {
            element.classList.remove('unlocked');
            element.classList.add('locked');
        }
    });
}

// ═══════════════════════════════════════════════════════════════
// UPDATE GOALS
// ═══════════════════════════════════════════════════════════════

function updateGoals(data) {
    const { goals } = data;

    // Weekly goal
    const weeklyPercent = (goals.weekly.current / goals.weekly.target) * 100;
    document.getElementById('weekly-goal-progress').style.width = `${weeklyPercent}%`;
    document.querySelector('.goal-card:nth-child(1) .goal-text').textContent =
        `${goals.weekly.current} / ${goals.weekly.target} видео`;

    // Monthly goal
    const monthlyPercent = (goals.monthly.current / goals.monthly.target) * 100;
    document.getElementById('monthly-goal-progress').style.width = `${monthlyPercent}%`;
    document.querySelector('.goal-card:nth-child(2) .goal-text').textContent =
        `${goals.monthly.current} / ${goals.monthly.target} видео`;
}

// ═══════════════════════════════════════════════════════════════
// EDIT GOAL
// ═══════════════════════════════════════════════════════════════

function editGoal(type) {
    const goalData = statsData.goals[type];
    const goalName = type === 'weekly' ? 'недельную' : 'месячную';

    const newTarget = prompt(`Введите новую ${goalName} цель:`, goalData.target);

    if (newTarget && !isNaN(newTarget) && newTarget > 0) {
        // TODO: Save to backend
        statsData.goals[type].target = parseInt(newTarget);
        updateGoals(statsData);
        alert(`✅ ${goalName.charAt(0).toUpperCase() + goalName.slice(1)} цель обновлена!`);
    }
}

// ═══════════════════════════════════════════════════════════════
// EXPORT FUNCTIONS
// ═══════════════════════════════════════════════════════════════

function exportToCSV() {
    if (!statsData) {
        alert('⚠️ Нет данных для экспорта');
        return;
    }

    // Create CSV content
    let csv = 'Метрика,Значение\n';
    csv += `Всего видео,${statsData.overview.totalVideos}\n`;
    csv += `Общее время (мин),${statsData.overview.totalTimeMinutes}\n`;
    csv += `Успешность (%),${statsData.overview.successRate}\n`;
    csv += `Средняя длина (сек),${statsData.overview.avgDurationSeconds}\n`;

    // Download
    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `youtube-automation-stats-${Date.now()}.csv`;
    link.click();
    URL.revokeObjectURL(url);

    alert('✅ Данные экспортированы в CSV!');
}

function exportToJSON() {
    if (!statsData) {
        alert('⚠️ Нет данных для экспорта');
        return;
    }

    // Download
    const dataStr = JSON.stringify(statsData, null, 2);
    const blob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `youtube-automation-stats-${Date.now()}.json`;
    link.click();
    URL.revokeObjectURL(url);

    alert('✅ Данные экспортированы в JSON!');
}

function exportToExcel() {
    alert('📗 Экспорт в Excel будет доступен в следующей версии!');
    // TODO: Implement Excel export using a library like SheetJS
}
