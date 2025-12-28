/**
 * Главный компонент Frontend приложения
 *
 * Функционал:
 * - Навигация между страницами
 * - Управление состоянием приложения
 * - Интеграция с Backend API
 * - Отображение уведомлений и статусов
 */

import React, { useState, useEffect } from 'react';
import './App.css';

function App() {
  const [apiStatus, setApiStatus] = useState(null);
  const [loading, setLoading] = useState(true);

  // Проверка состояния API при загрузке
  useEffect(() => {
    checkApiHealth();
  }, []);

  const checkApiHealth = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/health');
      const data = await response.json();
      setApiStatus(data);
    } catch (error) {
      console.error('Ошибка подключения к API:', error);
      setApiStatus({ status: 'error', message: 'Не удалось подключиться к серверу' });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>🎬 YouTube Automation</h1>
        <p>Автоматизированная система создания видео для faceless каналов</p>
      </header>

      <main className="App-main">
        {loading ? (
          <div className="loading">Загрузка...</div>
        ) : (
          <div className="dashboard">
            <section className="status-card">
              <h2>Статус системы</h2>
              {apiStatus && (
                <div className={`status ${apiStatus.status}`}>
                  <p><strong>API:</strong> {apiStatus.status}</p>
                  {apiStatus.services && (
                    <div className="services">
                      <p><strong>Сервисы:</strong></p>
                      <ul>
                        <li>YouTube API: {apiStatus.services.youtube_api ? '✅' : '❌'}</li>
                        <li>Claude API: {apiStatus.services.anthropic_api ? '✅' : '❌'}</li>
                        <li>OpenAI API: {apiStatus.services.openai_api ? '✅' : '❌'}</li>
                        <li>Stability AI: {apiStatus.services.stability_api ? '✅' : '❌'}</li>
                        <li>ElevenLabs: {apiStatus.services.elevenlabs_api ? '✅' : '❌'}</li>
                      </ul>
                    </div>
                  )}
                </div>
              )}
            </section>

            <section className="features">
              <h2>Функционал</h2>
              <div className="feature-grid">
                <div className="feature-card">
                  <h3>🔍 Анализ каналов</h3>
                  <p>Анализ популярных YouTube каналов и трендов</p>
                  <button disabled>Скоро...</button>
                </div>

                <div className="feature-card">
                  <h3>📝 Генерация скриптов</h3>
                  <p>Создание уникальных сценариев с помощью AI</p>
                  <button disabled>Скоро...</button>
                </div>

                <div className="feature-card">
                  <h3>🎨 Генерация изображений</h3>
                  <p>Создание визуального контента</p>
                  <button disabled>Скоро...</button>
                </div>

                <div className="feature-card">
                  <h3>🎤 Озвучка</h3>
                  <p>Профессиональная озвучка текста</p>
                  <button disabled>Скоро...</button>
                </div>

                <div className="feature-card">
                  <h3>🎬 Монтаж видео</h3>
                  <p>Автоматическая сборка видео</p>
                  <button disabled>Скоро...</button>
                </div>

                <div className="feature-card">
                  <h3>📊 Субтитры</h3>
                  <p>Генерация субтитров</p>
                  <button disabled>Скоро...</button>
                </div>
              </div>
            </section>

            <section className="quick-start">
              <h2>Быстрый старт</h2>
              <ol>
                <li>Убедитесь что Backend запущен (см. README.md)</li>
                <li>Настройте API ключи в файле .env</li>
                <li>Проверьте что все сервисы активны ✅</li>
                <li>Начните создавать контент!</li>
              </ol>
            </section>
          </div>
        )}
      </main>

      <footer className="App-footer">
        <p>YouTube Automation v1.0.0 | Made with AI 🤖</p>
      </footer>
    </div>
  );
}

export default App;
