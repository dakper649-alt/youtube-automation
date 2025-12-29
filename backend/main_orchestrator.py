"""
Главный оркестратор системы YouTube автоматизации

Объединяет все сервисы для создания полного пайплайна:
1. Анализ ниши и поиск лучших идей (ContentAnalyzer)
2. Генерация скрипта (ScriptGenerator)
3. Создание промптов для изображений (ScriptGenerator)
4. Генерация изображений (TODO)
5. Создание озвучки (TODO)
6. Монтаж видео (TODO)

Использует:
- APIKeyManager для централизованного управления ключами
- ContentAnalyzer для поиска идей
- YouTubeAnalyzer для анализа конкурентов
- ScriptGenerator для генерации контента
"""

import sys
import os
from pathlib import Path

# Добавляем путь к родительской директории для импорта
sys.path.insert(0, str(Path(__file__).parent))

from services.api_key_manager import APIKeyManager
from services.content_analyzer import ContentAnalyzer, ContentAnalyzerError
from services.analyzer import YouTubeAnalyzer, YouTubeAnalyzerError
from services.script_gen import ScriptGenerator, ScriptGeneratorError
from typing import Dict, List, Optional
from datetime import datetime
import asyncio
import json


class YouTubeAutomationError(Exception):
    """Базовый класс для ошибок автоматизации"""
    pass


class YouTubeAutomationOrchestrator:
    """
    Главный оркестратор системы YouTube автоматизации

    Координирует работу всех сервисов для создания видео от идеи до готового контента
    """

    def __init__(
        self,
        cache_file: str = ".api_keys_cache.json",
        keys_file: str = ".keys_secure.json"
    ):
        """
        Инициализация оркестратора

        Создаёт и настраивает все необходимые сервисы:
        - APIKeyManager: управление API ключами
        - YouTubeAnalyzer: анализ YouTube каналов
        - ContentAnalyzer: поиск идей для видео
        - ScriptGenerator: генерация скриптов

        Args:
            cache_file: Файл для кэша использования API ключей
            keys_file: Файл с API ключами

        Raises:
            YouTubeAutomationError: При ошибках инициализации
        """
        try:
            print("=" * 70)
            print("🚀 YOUTUBE AUTOMATION ORCHESTRATOR")
            print("=" * 70)
            print()

            # 1. Инициализируем менеджер API ключей
            print("⚙️  Инициализация APIKeyManager...")
            self.api_key_manager = APIKeyManager(
                cache_file=cache_file,
                keys_file=keys_file
            )
            print()

            # 2. Инициализируем YouTube Analyzer
            print("⚙️  Инициализация YouTubeAnalyzer...")
            try:
                youtube_key = self.api_key_manager.get_youtube_key()
                self.youtube_analyzer = YouTubeAnalyzer(youtube_key)
                print("   ✅ YouTubeAnalyzer инициализирован")
            except Exception as e:
                print(f"   ⚠️  YouTubeAnalyzer недоступен: {e}")
                self.youtube_analyzer = None

            # 3. Инициализируем Content Analyzer
            print("⚙️  Инициализация ContentAnalyzer...")
            self.content_analyzer = ContentAnalyzer(
                api_key_manager=self.api_key_manager,
                youtube_analyzer=self.youtube_analyzer
            )

            # 4. Инициализируем Script Generator
            print("⚙️  Инициализация ScriptGenerator...")
            gemini_key = self.api_key_manager.get_gemini_key()
            self.script_generator = ScriptGenerator(
                api_key=gemini_key,
                provider="gemini"
            )
            print("   ✅ ScriptGenerator инициализирован (Google Gemini)")

            # 5. Инициализируем Ken Burns Effects
            print("⚙️  Инициализация KenBurnsEffect...")
            from services.ken_burns import KenBurnsEffect
            self.ken_burns = KenBurnsEffect()
            print("   ✅ KenBurnsEffect инициализирован")

            print()
            print("=" * 70)
            print("✅ ВСЕ СЕРВИСЫ ИНИЦИАЛИЗИРОВАНЫ УСПЕШНО")
            print("=" * 70)
            print()

        except Exception as e:
            raise YouTubeAutomationError(f"Ошибка инициализации оркестратора: {str(e)}")

    def show_stats(self):
        """
        Показывает статистику использования API ключей

        Выводит:
        - Количество доступных ключей для каждого сервиса
        - Количество сделанных запросов
        - Доступность каждого сервиса
        """
        print("\n" + "=" * 70)
        self.api_key_manager.print_stats()
        print("=" * 70 + "\n")

    async def create_video_pipeline(
        self,
        niche: str,
        num_videos: int = 1,
        analyze_competitors: bool = True,
        video_length: int = 1000,
        style: str = 'educational',
        tone: str = 'professional',
        language: str = 'ru',
        image_style: str = 'minimalist_stick_figure'
    ) -> List[Dict]:
        """
        Полный пайплайн создания видео от идеи до готового контента

        Этапы:
        1. Поиск лучших идей в нише
        2. Генерация скрипта для каждой идеи
        3. Создание промптов для изображений
        4. [TODO] Генерация изображений
        5. [TODO] Создание озвучки
        6. [TODO] Монтаж видео

        Args:
            niche: Ниша для создания видео (например, "психология", "productivity")
            num_videos: Количество видео для создания (по умолчанию 1)
            analyze_competitors: Анализировать конкурентов (по умолчанию True)
            video_length: Целевая длина скрипта в словах (по умолчанию 1000)
            style: Стиль видео ('educational', 'entertaining', 'documentary')
            tone: Тон видео ('professional', 'casual', 'humorous')
            language: Язык ('ru', 'en')
            image_style: Стиль изображений (по умолчанию 'minimalist_stick_figure')

        Returns:
            List[Dict]: Список созданных видео проектов, каждый содержит:
                - idea: Идея видео
                - script: Сгенерированный скрипт
                - image_prompts: Промпты для изображений
                - status: Статус создания
                - created_at: Время создания

        Raises:
            YouTubeAutomationError: При ошибках создания
        """
        try:
            print("\n" + "=" * 70)
            print(f"🎬 ЗАПУСК ПАЙПЛАЙНА СОЗДАНИЯ ВИДЕО")
            print("=" * 70)
            print(f"   Ниша: {niche}")
            print(f"   Количество видео: {num_videos}")
            print(f"   Стиль: {style}")
            print(f"   Тон: {tone}")
            print(f"   Язык: {language}")
            print("=" * 70)
            print()

            video_projects = []

            # ЭТАП 1: Поиск лучших идей
            print("📋 ЭТАП 1: ПОИСК ЛУЧШИХ ИДЕЙ ДЛЯ ВИДЕО")
            print("-" * 70)

            ideas = await self.content_analyzer.find_best_video_ideas(
                niche=niche,
                num_ideas=num_videos * 2,  # Генерируем больше идей для выбора
                analyze_competitors=analyze_competitors
            )

            print(f"✅ Найдено {len(ideas)} идей")
            print()

            # Берём топ идей
            top_ideas = ideas[:num_videos]

            print(f"🎯 Выбраны ТОП-{num_videos} идей:")
            for i, idea in enumerate(top_ideas, 1):
                print(f"   {i}. {idea['title']}")
                print(f"      Вирусный потенциал: {idea['viral_score']}/100")
                print(f"      Сложность: {idea['difficulty']}")
                print()

            # ЭТАП 2-3: Генерация скрипта и промптов для каждой идеи
            for idx, idea in enumerate(top_ideas, 1):
                print("=" * 70)
                print(f"📹 ВИДЕО {idx}/{num_videos}: {idea['title']}")
                print("=" * 70)
                print()

                project = {
                    'idea': idea,
                    'script': None,
                    'image_prompts': None,
                    'images': None,  # TODO
                    'voiceover': None,  # TODO
                    'video': None,  # TODO
                    'status': 'in_progress',
                    'created_at': datetime.now().isoformat()
                }

                try:
                    # ЭТАП 2: Генерация скрипта
                    print("📝 ЭТАП 2: ГЕНЕРАЦИЯ СКРИПТА")
                    print("-" * 70)

                    script = await self.script_generator.generate_script(
                        topic=idea['title'],
                        target_length=video_length,
                        language=language,
                        style=style,
                        tone=tone
                    )

                    project['script'] = script

                    print(f"✅ Скрипт сгенерирован")
                    print(f"   Слов: {script['word_count']}")
                    print(f"   Примерная длительность: {script['estimated_duration']} сек")
                    print()

                    # Показываем превью скрипта
                    print("📄 Превью скрипта:")
                    print("-" * 70)
                    preview = script['script'][:300] + "..." if len(script['script']) > 300 else script['script']
                    print(preview)
                    print("-" * 70)
                    print()

                    # ЭТАП 3: Создание промптов для изображений
                    print("🖼️  ЭТАП 3: СОЗДАНИЕ ПРОМПТОВ ДЛЯ ИЗОБРАЖЕНИЙ")
                    print("-" * 70)

                    image_prompts = await self.script_generator.generate_image_prompts(
                        script=script['script'],
                        style=image_style,
                        images_per_minute=15
                    )

                    project['image_prompts'] = image_prompts

                    print(f"✅ Сгенерировано {len(image_prompts)} промптов для изображений")
                    print()

                    # Показываем несколько примеров промптов
                    print("🖼️  Примеры промптов:")
                    for i, prompt_data in enumerate(image_prompts[:3], 1):
                        print(f"   {i}. [{prompt_data['timestamp']}s] {prompt_data['prompt'][:80]}...")
                    if len(image_prompts) > 3:
                        print(f"   ... и ещё {len(image_prompts) - 3} промптов")
                    print()

                    # ЭТАП 4: Генерация изображений (TODO)
                    print("🎨 ЭТАП 4: ГЕНЕРАЦИЯ ИЗОБРАЖЕНИЙ")
                    print("-" * 70)
                    print("   ⏸️  TODO: Интеграция с Stable Diffusion / DALL-E")
                    print("   💡 Используйте промпты из image_prompts для генерации изображений")
                    print()

                    # ЭТАП 5: Создание озвучки (TODO)
                    print("🎤 ЭТАП 5: СОЗДАНИЕ ОЗВУЧКИ")
                    print("-" * 70)
                    print("   ⏸️  TODO: Интеграция с TTS сервисом (ElevenLabs / Google TTS)")
                    print("   💡 Используйте script['script'] для озвучки")
                    print()

                    # ЭТАП 6: Монтаж видео (TODO)
                    print("🎬 ЭТАП 6: МОНТАЖ ВИДЕО")
                    print("-" * 70)
                    print("   ⏸️  TODO: Интеграция с MoviePy / FFmpeg")
                    print("   💡 Соберите изображения и озвучку в финальное видео")
                    print()

                    # Успешно завершено
                    project['status'] = 'completed'
                    print("✅ Видео проект создан успешно!")
                    print()

                except Exception as e:
                    project['status'] = 'failed'
                    project['error'] = str(e)
                    print(f"❌ Ошибка создания видео: {e}")
                    print()

                video_projects.append(project)

            # Итоговая статистика
            print("=" * 70)
            print("📊 ИТОГОВАЯ СТАТИСТИКА")
            print("=" * 70)

            successful = sum(1 for p in video_projects if p['status'] == 'completed')
            failed = sum(1 for p in video_projects if p['status'] == 'failed')

            print(f"   ✅ Успешно создано: {successful}/{num_videos}")
            if failed > 0:
                print(f"   ❌ Не удалось создать: {failed}/{num_videos}")

            print()
            print("📁 Результаты сохранены в переменной video_projects")
            print()

            # Показываем статистику API
            self.show_stats()

            return video_projects

        except Exception as e:
            raise YouTubeAutomationError(f"Ошибка пайплайна создания видео: {str(e)}")

    async def analyze_niche(self, niche: str) -> Dict:
        """
        Полный анализ ниши

        Включает:
        - Поиск лучших идей
        - Анализ сезонных трендов
        - Рекомендации по контенту

        Args:
            niche: Ниша для анализа

        Returns:
            Dict: Полный анализ ниши

        Raises:
            YouTubeAutomationError: При ошибках анализа
        """
        try:
            print("\n" + "=" * 70)
            print(f"🔍 ПОЛНЫЙ АНАЛИЗ НИШИ: {niche}")
            print("=" * 70)
            print()

            # 1. Поиск идей
            print("📋 1. Поиск лучших идей...")
            ideas = await self.content_analyzer.find_best_video_ideas(
                niche=niche,
                num_ideas=10,
                analyze_competitors=True
            )

            # 2. Анализ сезонных трендов
            print("📈 2. Анализ сезонных трендов...")
            trends = await self.content_analyzer.analyze_seasonal_trends(niche)

            # 3. Формируем отчёт
            report = {
                'niche': niche,
                'top_ideas': ideas[:5],
                'seasonal_trends': trends,
                'recommendations': {
                    'best_idea': ideas[0] if ideas else None,
                    'best_time_to_publish': trends.get('best_time_to_publish', 'Неизвестно'),
                    'rising_topics': trends.get('rising_topics', []),
                    'current_trends': trends.get('current_trends', [])
                },
                'analyzed_at': datetime.now().isoformat()
            }

            # 4. Выводим отчёт
            print("\n" + "=" * 70)
            print("📊 ОТЧЁТ ПО НИШЕ")
            print("=" * 70)
            print()

            print("🏆 ТОП-5 ИДЕЙ:")
            for i, idea in enumerate(ideas[:5], 1):
                print(f"   {i}. {idea['title']}")
                print(f"      Вирусный потенциал: {idea['viral_score']}/100")
                print(f"      Аудитория: {idea['target_audience']}")
                print()

            print("📈 СЕЗОННЫЕ ТРЕНДЫ:")
            print(f"   Текущие тренды: {', '.join(trends.get('current_trends', [])[:5])}")
            print(f"   Растущие темы: {', '.join(trends.get('rising_topics', [])[:5])}")
            print(f"   Лучшее время публикации: {trends.get('best_time_to_publish', 'Неизвестно')}")
            print()

            if trends.get('seasonal_insights'):
                print("💡 СЕЗОННЫЕ ИНСАЙТЫ:")
                print(f"   {trends['seasonal_insights']}")
                print()

            print("=" * 70)
            print()

            return report

        except Exception as e:
            raise YouTubeAutomationError(f"Ошибка анализа ниши: {str(e)}")

    def save_project(self, project: Dict, output_file: str):
        """
        Сохраняет проект видео в JSON файл

        Args:
            project: Данные проекта
            output_file: Путь к файлу для сохранения

        Raises:
            YouTubeAutomationError: При ошибках сохранения
        """
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(project, f, ensure_ascii=False, indent=2)

            print(f"💾 Проект сохранён в {output_file}")

        except Exception as e:
            raise YouTubeAutomationError(f"Ошибка сохранения проекта: {str(e)}")

    def load_project(self, input_file: str) -> Dict:
        """
        Загружает проект из JSON файла

        Args:
            input_file: Путь к файлу проекта

        Returns:
            Dict: Данные проекта

        Raises:
            YouTubeAutomationError: При ошибках загрузки
        """
        try:
            with open(input_file, 'r', encoding='utf-8') as f:
                project = json.load(f)

            print(f"📂 Проект загружен из {input_file}")
            return project

        except Exception as e:
            raise YouTubeAutomationError(f"Ошибка загрузки проекта: {str(e)}")

    async def create_full_video(
        self,
        topic: str,
        niche: str,
        style: str = "minimalist_stick_figure",
        voice: str = "rachel",
        subtitle_style: str = "highlighted_words",
        on_progress: callable = None
    ) -> str:
        """
        ПОЛНЫЙ ПАЙПЛАЙН: от темы до готового видео!

        Args:
            topic: Тема видео
            niche: Ниша
            style: Стиль изображений
            voice: Голос для озвучки
            subtitle_style: Стиль субтитров
            on_progress: Callback для обновления прогресса

        Returns:
            Путь к готовому видео
        """

        from services.video_editor import VideoEditor
        from services.subtitle_gen import SubtitleGenerator

        print(f"\n🎬 ПОЛНЫЙ ПАЙПЛАЙН СОЗДАНИЯ ВИДЕО")
        print(f"=" * 80)
        print(f"📌 Тема: {topic}")
        print(f"🎨 Стиль изображений: {style}")
        print(f"🎙️ Голос: {voice}")
        print(f"📝 Субтитры: {subtitle_style}")
        print(f"=" * 80)

        # Создаём папку для проекта
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        project_dir = f"./output/{timestamp}_{topic[:30].replace(' ', '_')}"
        os.makedirs(project_dir, exist_ok=True)
        os.makedirs(f"{project_dir}/images", exist_ok=True)

        try:
            # ШАГ 1: Генерация скрипта
            if on_progress:
                on_progress("generating_script")
            print(f"\n[1/5] ✍️ Генерация скрипта...")

            script_result = await self.script_generator.generate_script(
                topic=topic,
                target_length=1000,
                language='ru'
            )

            script_text = script_result['script']

            # Сохраняем скрипт
            with open(f"{project_dir}/script.txt", 'w', encoding='utf-8') as f:
                f.write(f"HOOK:\n{script_result['hook']}\n\n")
                f.write(f"СКРИПТ:\n{script_text}\n\n")
                f.write(f"CTA:\n{script_result['cta']}\n\n")
                f.write(f"ЗАГОЛОВКИ:\n" + '\n'.join(script_result['title_suggestions']))

            print(f"   ✅ Скрипт: {script_result['word_count']} слов")

            # ШАГ 2: Генерация промптов для изображений
            if on_progress:
                on_progress("generating_images")
            print(f"\n[2/5] 🎨 Генерация изображений...")

            image_prompts = await self.script_generator.generate_image_prompts(
                script=script_text,
                style=style,
                images_per_minute=15
            )

            # Генерируем изображения
            from services.image_gen import ImageGenerator
            image_gen = ImageGenerator(self.api_key_manager)

            scenes = await image_gen.generate_images_for_script(
                script=script_text,
                image_prompts=image_prompts,
                style=style,
                output_dir=f"{project_dir}/images"
            )

            print(f"   ✅ Изображений: {len(scenes)}")

            # ШАГ 3: Применение Ken Burns эффектов
            print(f"\n[3/5] 🎬 Применение Ken Burns эффектов...")
            scenes = self.ken_burns.process_scenes(scenes, script_result)

            # ШАГ 4: Генерация озвучки
            if on_progress:
                on_progress("generating_audio")
            print(f"\n[4/5] 🎙️ Генерация озвучки...")

            from services.voice_manager import VoiceManager
            from services.text_normalizer import TextNormalizer

            normalizer = TextNormalizer(language='ru')
            voice_manager = VoiceManager(self.api_key_manager, normalizer)

            audio_path = await voice_manager.generate_audio(
                text=script_text,
                voice_id=voice,
                output_path=f"{project_dir}/audio.mp3"
            )

            # ШАГ 5: Финальный монтаж
            if on_progress:
                on_progress("editing_video")
            print(f"\n[5/5] 🎞️ Финальный монтаж...")

            subtitle_gen = SubtitleGenerator()
            video_editor = VideoEditor(self.ken_burns, subtitle_gen)

            output_video = video_editor.create_video(
                scenes=scenes,
                audio_path=audio_path,
                output_path=f"{project_dir}/video.mp4",
                subtitle_text=script_text,
                subtitle_style=subtitle_style,
                add_transitions=True
            )

            print(f"\n🎉 ВИДЕО ГОТОВО!")
            print(f"📁 Папка проекта: {project_dir}")
            print(f"🎬 Видео: {output_video}")

            return output_video

        except Exception as e:
            print(f"\n❌ ОШИБКА: {e}")
            raise
