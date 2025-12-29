"""
Модуль для анализа контента и поиска лучших идей для YouTube видео

Функционал:
- Поиск трендовых и вирусных идей для видео
- Анализ конкурентов и их успешного контента
- Извлечение паттернов из популярных тем
- Генерация новых идей на основе паттернов
- Ранжирование идей по вирусному потенциалу
- Анализ сезонных трендов

Использует:
- YouTube Data API для анализа видео
- Google Gemini для генерации идей
- APIKeyManager для управления ключами
"""

import sys
import os
from pathlib import Path

# Добавляем путь к родительской директории для импорта
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.api_key_manager import APIKeyManager
from services.analyzer import YouTubeAnalyzer, YouTubeAnalyzerError
import google.generativeai as genai
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from collections import Counter
import re
import asyncio


class ContentAnalyzerError(Exception):
    """Базовый класс для ошибок анализатора контента"""
    pass


class ContentAnalyzer:
    """
    Класс для анализа контента и поиска лучших идей для видео

    Использует YouTube API для анализа трендов и Google Gemini для генерации идей
    """

    def __init__(
        self,
        api_key_manager: APIKeyManager,
        youtube_analyzer: Optional[YouTubeAnalyzer] = None
    ):
        """
        Инициализация анализатора контента

        Args:
            api_key_manager: Менеджер API ключей
            youtube_analyzer: YouTube анализатор (опционально, создаётся автоматически)

        Raises:
            ContentAnalyzerError: При ошибках инициализации
        """
        try:
            self.api_key_manager = api_key_manager

            # Инициализируем YouTube анализатор
            if youtube_analyzer:
                self.youtube_analyzer = youtube_analyzer
            else:
                youtube_key = self.api_key_manager.get_youtube_key()
                self.youtube_analyzer = YouTubeAnalyzer(youtube_key)

            # Инициализируем Gemini клиент
            gemini_key = self.api_key_manager.get_gemini_key()
            genai.configure(api_key=gemini_key)
            self.gemini_model = genai.GenerativeModel("gemini-1.5-flash")

            print("✅ ContentAnalyzer инициализирован")

        except Exception as e:
            raise ContentAnalyzerError(f"Ошибка инициализации ContentAnalyzer: {str(e)}")

    async def find_best_video_ideas(
        self,
        niche: str,
        num_ideas: int = 10,
        analyze_competitors: bool = True
    ) -> List[Dict]:
        """
        Находит лучшие идеи для видео в заданной нише

        Процесс:
        1. Анализирует топовые видео в нише (если analyze_competitors=True)
        2. Извлекает паттерны успешного контента
        3. Генерирует новые идеи на основе паттернов
        4. Ранжирует идеи по вирусному потенциалу

        Args:
            niche: Ниша (тема) для анализа (например, "психология", "productivity")
            num_ideas: Количество идей для генерации (по умолчанию 10)
            analyze_competitors: Анализировать конкурентов (по умолчанию True)

        Returns:
            List[Dict]: Список идей, каждая содержит:
                - title: Заголовок видео
                - description: Краткое описание
                - viral_score: Оценка вирусного потенциала (0-100)
                - target_audience: Целевая аудитория
                - hook: Захватывающий хук для видео
                - estimated_views: Примерные просмотры
                - difficulty: Сложность создания (easy/medium/hard)

        Raises:
            ContentAnalyzerError: При ошибках анализа
        """
        try:
            print(f"\n🔍 Анализирую нишу: {niche}")
            print(f"   Генерирую {num_ideas} идей...")

            patterns = {}
            trending_topics = []

            # Шаг 1: Анализ конкурентов (если включён)
            if analyze_competitors:
                print("   📊 Анализирую конкурентов...")

                # Ищем топовые видео в нише
                try:
                    request = self.youtube_analyzer.youtube.search().list(
                        part='snippet',
                        q=niche,
                        type='video',
                        maxResults=20,
                        order='viewCount',
                        publishedAfter=(datetime.now() - timedelta(days=90)).isoformat() + 'Z'
                    )
                    response = request.execute()

                    # Собираем темы из успешных видео
                    trending_topics = []
                    video_performances = []

                    for item in response['items']:
                        video_id = item['id']['videoId']
                        title = item['snippet']['title']
                        trending_topics.append({
                            'title': title,
                            'video_id': video_id
                        })

                        # Получаем метрики видео
                        try:
                            performance = await self.youtube_analyzer.analyze_video_performance(video_id)
                            video_performances.append({
                                'title': title,
                                'performance': self._calculate_performance(performance)
                            })
                        except:
                            continue

                    print(f"   ✅ Найдено {len(trending_topics)} трендовых видео")

                    # Извлекаем паттерны
                    patterns = self._extract_patterns(trending_topics)

                except Exception as e:
                    print(f"   ⚠️  Ошибка анализа конкурентов: {e}")
                    # Продолжаем без анализа конкурентов

            # Шаг 2: Генерация идей
            print("   🤖 Генерирую идеи с помощью AI...")
            ideas = await self._generate_ideas_from_patterns(patterns, niche, num_ideas)

            # Шаг 3: Ранжирование по вирусному потенциалу
            print("   📈 Ранжирую идеи по вирусному потенциалу...")
            ranked_ideas = self._rank_by_viral_potential(ideas)

            print(f"   ✅ Сгенерировано {len(ranked_ideas)} идей\n")

            return ranked_ideas

        except Exception as e:
            raise ContentAnalyzerError(f"Ошибка поиска идей: {str(e)}")

    def _calculate_performance(self, video: Dict) -> float:
        """
        Вычисляет performance score видео

        Учитывает:
        - Просмотры
        - Engagement rate
        - Соотношение лайков к просмотрам

        Args:
            video: Словарь с метриками видео

        Returns:
            float: Performance score (0-100)
        """
        try:
            views = video.get('views', 0)
            likes = video.get('likes', 0)
            comments = video.get('comments', 0)
            engagement_rate = video.get('engagement_rate', 0)

            # Базовый score на основе просмотров (логарифмическая шкала)
            import math
            views_score = min(100, math.log10(views + 1) * 20) if views > 0 else 0

            # Engagement score
            engagement_score = min(100, engagement_rate * 20)

            # Like rate score
            like_rate = (likes / views * 100) if views > 0 else 0
            like_score = min(100, like_rate * 20)

            # Итоговый score (взвешенная сумма)
            total_score = (
                views_score * 0.4 +      # 40% вес на просмотры
                engagement_score * 0.4 + # 40% вес на engagement
                like_score * 0.2         # 20% вес на лайки
            )

            return round(total_score, 2)

        except Exception as e:
            return 0.0

    def _extract_patterns(self, topics: List[Dict]) -> Dict:
        """
        Извлекает паттерны из успешных тем

        Анализирует:
        - Частые слова в заголовках
        - Длину заголовков
        - Использование вопросов
        - Использование чисел
        - Эмоциональные триггеры

        Args:
            topics: Список тем с заголовками

        Returns:
            Dict: Паттерны успешного контента
        """
        try:
            if not topics:
                return {}

            titles = [t['title'] for t in topics]

            # Извлекаем слова
            all_words = []
            for title in titles:
                words = re.findall(r'\b[A-Za-zА-Яа-я]{3,}\b', title.lower())
                all_words.extend(words)

            # Стоп-слова
            stop_words = {
                'the', 'and', 'for', 'are', 'but', 'not', 'you', 'all', 'this', 'that',
                'это', 'как', 'для', 'что', 'или', 'все', 'был', 'быть', 'так'
            }

            filtered_words = [w for w in all_words if w not in stop_words]
            word_counter = Counter(filtered_words)

            # Топ слова
            top_words = [word for word, count in word_counter.most_common(10)]

            # Анализируем паттерны заголовков
            has_questions = sum(1 for t in titles if '?' in t)
            has_numbers = sum(1 for t in titles if re.search(r'\d+', t))
            avg_length = sum(len(t) for t in titles) / len(titles) if titles else 0

            # Эмоциональные триггеры
            emotion_triggers = {
                'shocking': sum(1 for t in titles if any(word in t.lower() for word in ['shocking', 'шокирующ', 'невероятн'])),
                'secret': sum(1 for t in titles if any(word in t.lower() for word in ['secret', 'секрет', 'скрыт'])),
                'ultimate': sum(1 for t in titles if any(word in t.lower() for word in ['ultimate', 'best', 'top', 'лучш', 'топ'])),
                'how_to': sum(1 for t in titles if any(word in t.lower() for word in ['how to', 'как']))
            }

            return {
                'top_keywords': top_words,
                'avg_title_length': int(avg_length),
                'question_percentage': round(has_questions / len(titles) * 100, 1),
                'number_percentage': round(has_numbers / len(titles) * 100, 1),
                'emotion_triggers': emotion_triggers,
                'sample_titles': titles[:5]  # Примеры успешных заголовков
            }

        except Exception as e:
            print(f"   ⚠️  Ошибка извлечения паттернов: {e}")
            return {}

    async def _generate_ideas_from_patterns(
        self,
        patterns: Dict,
        niche: str,
        num_ideas: int
    ) -> List[Dict]:
        """
        Генерирует идеи на основе паттернов с помощью Google Gemini

        Args:
            patterns: Паттерны успешного контента
            niche: Ниша
            num_ideas: Количество идей

        Returns:
            List[Dict]: Список идей

        Raises:
            ContentAnalyzerError: При ошибках генерации
        """
        try:
            # Строим промпт для Gemini
            patterns_desc = ""
            if patterns:
                patterns_desc = f"""
ПАТТЕРНЫ УСПЕШНОГО КОНТЕНТА В НИШЕ:
- Популярные ключевые слова: {', '.join(patterns.get('top_keywords', [])[:5])}
- Средняя длина заголовка: {patterns.get('avg_title_length', 50)} символов
- Вопросы в заголовках: {patterns.get('question_percentage', 0)}%
- Числа в заголовках: {patterns.get('number_percentage', 0)}%

ПРИМЕРЫ УСПЕШНЫХ ЗАГОЛОВКОВ:
{chr(10).join('- ' + t for t in patterns.get('sample_titles', [])[:3])}
"""

            prompt = f"""
Ты - эксперт по YouTube и вирусному контенту. Генерируй {num_ideas} УНИКАЛЬНЫХ идей для видео в нише "{niche}".

{patterns_desc}

ТРЕБОВАНИЯ К ИДЕЯМ:
1. Каждая идея должна быть УНИКАЛЬНОЙ и КЛИКАБЕЛЬНОЙ
2. Заголовок должен вызывать любопытство или обещать пользу
3. Учитывай найденные паттерны успешного контента
4. Используй эмоциональные триггеры (удивление, любопытство, польза)
5. Будь конкретным и избегай общих фраз

ФОРМАТ ОТВЕТА (строго следуй этой структуре для КАЖДОЙ идеи):

[IDEA 1]
Title: <Кликабельный заголовок видео>
Description: <Краткое описание в 1-2 предложениях>
Target Audience: <Целевая аудитория>
Hook: <Захватывающий хук для первых 10 секунд>
Difficulty: <easy/medium/hard>

[IDEA 2]
Title: <Кликабельный заголовок видео>
Description: <Краткое описание в 1-2 предложениях>
Target Audience: <Целевая аудитория>
Hook: <Захватывающий хук для первых 10 секунд>
Difficulty: <easy/medium/hard>

... и так далее для всех {num_ideas} идей.

ВАЖНО: Генерируй все {num_ideas} идей! Не останавливайся раньше.

Начинай генерацию!
"""

            # Вызываем Gemini API
            response = self.gemini_model.generate_content(prompt)
            response_text = response.text

            # Парсим ответ
            ideas = self._parse_ideas_response(response_text)

            if len(ideas) < num_ideas:
                print(f"   ⚠️  Сгенерировано только {len(ideas)} из {num_ideas} идей")

            return ideas

        except Exception as e:
            raise ContentAnalyzerError(f"Ошибка генерации идей: {str(e)}")

    def _parse_ideas_response(self, response_text: str) -> List[Dict]:
        """
        Парсит ответ Gemini и извлекает идеи

        Args:
            response_text: Текст ответа от Gemini

        Returns:
            List[Dict]: Список идей
        """
        ideas = []

        try:
            # Разбиваем на отдельные идеи
            idea_blocks = re.split(r'\[IDEA \d+\]', response_text)

            for block in idea_blocks:
                if not block.strip():
                    continue

                # Извлекаем поля
                title_match = re.search(r'Title:\s*(.+)', block)
                desc_match = re.search(r'Description:\s*(.+?)(?=Target Audience:|Hook:|Difficulty:|$)', block, re.DOTALL)
                audience_match = re.search(r'Target Audience:\s*(.+)', block)
                hook_match = re.search(r'Hook:\s*(.+?)(?=Difficulty:|$)', block, re.DOTALL)
                difficulty_match = re.search(r'Difficulty:\s*(\w+)', block)

                if title_match:
                    idea = {
                        'title': title_match.group(1).strip(),
                        'description': desc_match.group(1).strip() if desc_match else "",
                        'target_audience': audience_match.group(1).strip() if audience_match else "Широкая аудитория",
                        'hook': hook_match.group(1).strip() if hook_match else "",
                        'difficulty': difficulty_match.group(1).strip().lower() if difficulty_match else "medium",
                        'viral_score': 0,  # Будет вычислен позже
                        'estimated_views': 0  # Будет вычислен позже
                    }
                    ideas.append(idea)

            return ideas

        except Exception as e:
            print(f"   ⚠️  Ошибка парсинга идей: {e}")
            return []

    def _rank_by_viral_potential(self, ideas: List[Dict]) -> List[Dict]:
        """
        Ранжирует идеи по вирусному потенциалу

        Факторы вирусности:
        - Наличие триггеров в заголовке
        - Длина заголовка (оптимум 40-70 символов)
        - Наличие чисел
        - Наличие вопросов
        - Эмоциональная окраска
        - Конкретность vs абстрактность

        Args:
            ideas: Список идей

        Returns:
            List[Dict]: Отсортированный список идей с viral_score
        """
        try:
            for idea in ideas:
                score = 50  # Базовый score
                title = idea['title']

                # 1. Оптимальная длина заголовка (+20 баллов)
                title_length = len(title)
                if 40 <= title_length <= 70:
                    score += 20
                elif 30 <= title_length <= 80:
                    score += 10

                # 2. Наличие чисел (+15 баллов)
                if re.search(r'\d+', title):
                    score += 15

                # 3. Вопрос в заголовке (+15 баллов)
                if '?' in title:
                    score += 15

                # 4. Эмоциональные триггеры (+10 баллов каждый, макс 30)
                triggers = {
                    'шокирующ': ['шок', 'невероятн', 'удивительн', 'shocking', 'unbelievable'],
                    'секрет': ['секрет', 'скрыт', 'secret', 'hidden'],
                    'топ': ['лучш', 'топ', 'best', 'top', 'ultimate'],
                    'как': ['как', 'how to', 'guide'],
                    'почему': ['почему', 'why', 'reason']
                }

                trigger_count = 0
                for trigger_type, keywords in triggers.items():
                    if any(keyword in title.lower() for keyword in keywords):
                        score += 10
                        trigger_count += 1
                        if trigger_count >= 3:
                            break

                # 5. Наличие Hook (+10 баллов)
                if idea.get('hook'):
                    score += 10

                # 6. Простота создания (easy +5, medium 0, hard -5)
                difficulty = idea.get('difficulty', 'medium')
                if difficulty == 'easy':
                    score += 5
                elif difficulty == 'hard':
                    score -= 5

                # Ограничиваем score до 100
                score = min(100, score)

                # Сохраняем score
                idea['viral_score'] = score

                # Примерная оценка просмотров на основе score
                import random
                base_views = 1000 if difficulty == 'easy' else 500 if difficulty == 'medium' else 300
                idea['estimated_views'] = int(base_views * (score / 50) * random.uniform(0.8, 1.5))

            # Сортируем по viral_score
            ideas.sort(key=lambda x: x['viral_score'], reverse=True)

            return ideas

        except Exception as e:
            print(f"   ⚠️  Ошибка ранжирования: {e}")
            return ideas

    async def analyze_seasonal_trends(self, niche: str) -> Dict:
        """
        Анализирует сезонные тренды в нише

        Определяет:
        - Текущие тренды (последние 7 дней)
        - Растущие темы
        - Рекомендации по времени публикации

        Args:
            niche: Ниша для анализа

        Returns:
            Dict: Информация о трендах
                - current_trends: Список текущих трендов
                - rising_topics: Растущие темы
                - best_time_to_publish: Рекомендованное время
                - seasonal_insights: Сезонные инсайты

        Raises:
            ContentAnalyzerError: При ошибках анализа
        """
        try:
            print(f"\n🔍 Анализирую сезонные тренды в нише: {niche}")

            # Получаем недавние видео (последние 7 дней)
            request = self.youtube_analyzer.youtube.search().list(
                part='snippet',
                q=niche,
                type='video',
                maxResults=30,
                order='date',
                publishedAfter=(datetime.now() - timedelta(days=7)).isoformat() + 'Z'
            )
            response = request.execute()

            # Собираем заголовки
            recent_titles = [item['snippet']['title'] for item in response['items']]

            # Извлекаем ключевые слова
            all_words = []
            for title in recent_titles:
                words = re.findall(r'\b[A-Za-zА-Яа-я]{4,}\b', title.lower())
                all_words.extend(words)

            # Стоп-слова
            stop_words = {
                'the', 'and', 'for', 'are', 'but', 'not', 'you', 'all', 'this', 'that',
                'это', 'как', 'для', 'что', 'или', 'все', 'был', 'быть'
            }

            filtered_words = [w for w in all_words if w not in stop_words]
            word_counter = Counter(filtered_words)

            current_trends = [word for word, count in word_counter.most_common(10)]

            # Генерируем сезонные инсайты с помощью AI
            month = datetime.now().strftime('%B')

            prompt = f"""
Проанализируй сезонные тренды для ниши "{niche}" в месяце {month}.

ТЕКУЩИЕ ПОПУЛЯРНЫЕ ТЕМЫ: {', '.join(current_trends[:5])}

Дай краткие рекомендации:
1. Какие темы сейчас актуальны?
2. Какие темы будут расти в ближайшие 2-4 недели?
3. Лучшее время для публикации видео в этой нише (день недели и время)?

Ответ дай в формате:

[CURRENT]
<Список актуальных тем через запятую>

[RISING]
<Список растущих тем через запятую>

[TIMING]
<Рекомендация по времени публикации>

[INSIGHTS]
<Краткие сезонные инсайты 2-3 предложения>
"""

            response = self.gemini_model.generate_content(prompt)
            result_text = response.text

            # Парсим результат
            current_match = re.search(r'\[CURRENT\](.*?)(?=\[|$)', result_text, re.DOTALL)
            rising_match = re.search(r'\[RISING\](.*?)(?=\[|$)', result_text, re.DOTALL)
            timing_match = re.search(r'\[TIMING\](.*?)(?=\[|$)', result_text, re.DOTALL)
            insights_match = re.search(r'\[INSIGHTS\](.*?)(?=\[|$)', result_text, re.DOTALL)

            return {
                'current_trends': [t.strip() for t in current_match.group(1).split(',') if t.strip()] if current_match else current_trends,
                'rising_topics': [t.strip() for t in rising_match.group(1).split(',') if t.strip()] if rising_match else [],
                'best_time_to_publish': timing_match.group(1).strip() if timing_match else "Середина недели, 14:00-18:00",
                'seasonal_insights': insights_match.group(1).strip() if insights_match else "",
                'analyzed_at': datetime.now().isoformat()
            }

        except Exception as e:
            raise ContentAnalyzerError(f"Ошибка анализа сезонных трендов: {str(e)}")
