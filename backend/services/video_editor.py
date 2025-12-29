"""
Video Editor - финальный монтаж видео
Склейка изображений + аудио + Ken Burns + субтитры + переходы
"""

import os
from typing import List, Dict, Optional
from moviepy.editor import (
    ImageClip, AudioFileClip, CompositeVideoClip,
    concatenate_videoclips, TextClip, VideoClip
)
from moviepy.video.fx.all import resize, fadein, fadeout
import numpy as np


class VideoEditor:
    """
    Профессиональный видео редактор

    Возможности:
    - Ken Burns эффекты на изображениях
    - Плавные переходы между сценами
    - Субтитры с разными стилями
    - Синхронизация с аудио
    - Финальный рендер в высоком качестве
    """

    def __init__(self, ken_burns, subtitle_generator):
        self.ken_burns = ken_burns
        self.subtitle_gen = subtitle_generator

        # Настройки видео
        self.resolution = (1920, 1080)  # Full HD
        self.fps = 30

        # Типы переходов
        self.transitions = {
            'crossfade': 0.5,
            'crossfade_slow': 1.0,
            'fade_through_black': 0.8,
            'fade_through_white': 0.8
        }

    def create_video(
        self,
        scenes: List[Dict],
        audio_path: str,
        output_path: str,
        subtitle_text: str = None,
        subtitle_style: str = 'highlighted_words',
        add_transitions: bool = True
    ) -> str:
        """
        Создаёт финальное видео

        Args:
            scenes: Список сцен с изображениями и Ken Burns эффектами
            audio_path: Путь к аудио файлу
            output_path: Путь для сохранения видео
            subtitle_text: Текст для субтитров
            subtitle_style: Стиль субтитров
            add_transitions: Добавлять ли переходы

        Returns:
            Путь к готовому видео
        """

        print(f"\n🎬 СОЗДАНИЕ ВИДЕО")
        print(f"=" * 80)

        # 1. Загружаем аудио
        print(f"\n[1/6] 🎵 Загрузка аудио...")
        audio = AudioFileClip(audio_path)
        total_duration = audio.duration
        print(f"   Длительность аудио: {total_duration:.1f}s")

        # 2. Создаём видео клипы из изображений с Ken Burns
        print(f"\n[2/6] 🎨 Применение Ken Burns эффектов...")
        video_clips = self._create_clips_with_ken_burns(scenes, total_duration)

        # 3. Добавляем переходы
        if add_transitions:
            print(f"\n[3/6] 🔄 Добавление плавных переходов...")
            video_clips = self._add_transitions(video_clips, scenes)

        # 4. Склеиваем все клипы
        print(f"\n[4/6] 🎞️ Склейка всех сцен...")
        final_video = concatenate_videoclips(video_clips, method='compose')

        # Обрезаем до длины аудио если нужно
        if final_video.duration > total_duration:
            final_video = final_video.subclip(0, total_duration)

        # 5. Добавляем субтитры
        if subtitle_text:
            print(f"\n[5/6] 📝 Добавление субтитров...")
            final_video = self._add_subtitles(
                final_video,
                subtitle_text,
                subtitle_style,
                total_duration
            )

        # 6. Добавляем аудио
        print(f"\n[6/6] 🎵 Синхронизация с аудио...")
        final_video = final_video.set_audio(audio)

        # Рендер
        print(f"\n🎬 РЕНДЕРИНГ ВИДЕО...")
        print(f"   Разрешение: {self.resolution[0]}x{self.resolution[1]}")
        print(f"   FPS: {self.fps}")
        print(f"   Выходной файл: {output_path}")
        print(f"\n⏳ Это может занять несколько минут...")

        final_video.write_videofile(
            output_path,
            fps=self.fps,
            codec='libx264',
            audio_codec='aac',
            preset='medium',
            bitrate='8000k',
            threads=4,
            logger=None  # Отключаем verbose логи
        )

        # Очистка
        final_video.close()
        audio.close()
        for clip in video_clips:
            clip.close()

        print(f"\n✅ ВИДЕО ГОТОВО: {output_path}")

        # Статистика
        file_size_mb = os.path.getsize(output_path) / (1024 * 1024)
        print(f"📊 Размер файла: {file_size_mb:.1f} MB")
        print(f"⏱️ Длительность: {total_duration:.1f}s")
        print(f"=" * 80)

        return output_path

    def _create_clips_with_ken_burns(
        self,
        scenes: List[Dict],
        total_duration: float
    ) -> List[VideoClip]:
        """Создаёт видео клипы с Ken Burns эффектами"""

        clips = []

        for i, scene in enumerate(scenes):
            print(f"   [{i+1}/{len(scenes)}] {scene.get('effect_type', 'unknown')}")

            # Загружаем изображение
            img_clip = ImageClip(scene['path'])

            # Устанавливаем длительность
            duration = scene.get('duration', 5.0)
            img_clip = img_clip.set_duration(duration)

            # Применяем Ken Burns эффект
            effect_config = scene.get('effect_config')
            if effect_config:
                img_clip = self._apply_ken_burns_effect(img_clip, effect_config, duration)

            # Resize до нужного разрешения
            img_clip = img_clip.resize(self.resolution)

            clips.append(img_clip)

        return clips

    def _apply_ken_burns_effect(
        self,
        clip: ImageClip,
        config: Dict,
        duration: float
    ) -> VideoClip:
        """Применяет Ken Burns эффект к клипу"""

        start_scale = config['start_scale']
        end_scale = config['end_scale']
        start_pos = config['start_position']
        end_pos = config['end_position']

        def make_frame(t):
            """Создаёт кадр с интерполированным zoom и pan"""

            # Прогресс (0.0 - 1.0)
            progress = t / duration

            # Интерполяция scale
            scale = start_scale + (end_scale - start_scale) * progress

            # Интерполяция position
            pos_x = start_pos[0] + (end_pos[0] - start_pos[0]) * progress
            pos_y = start_pos[1] + (end_pos[1] - start_pos[1]) * progress

            # Получаем исходный кадр
            frame = clip.get_frame(0)
            h, w = frame.shape[:2]

            # Применяем zoom
            new_w = int(w * scale)
            new_h = int(h * scale)

            # Ресайз
            from PIL import Image
            img = Image.fromarray(frame)
            img_scaled = img.resize((new_w, new_h), Image.LANCZOS)

            # Crop по позиции
            crop_x = int((new_w - w) * pos_x)
            crop_y = int((new_h - h) * pos_y)

            img_cropped = img_scaled.crop((
                crop_x,
                crop_y,
                crop_x + w,
                crop_y + h
            ))

            return np.array(img_cropped)

        # Создаём новый клип с эффектом
        return VideoClip(make_frame, duration=duration)

    def _add_transitions(
        self,
        clips: List[VideoClip],
        scenes: List[Dict]
    ) -> List[VideoClip]:
        """Добавляет плавные переходы между клипами"""

        transition_clips = []

        for i, clip in enumerate(clips):
            # Определяем тип перехода на основе типа сцены
            scene_type = scenes[i].get('scene_type', 'regular')

            # Выбираем transition
            if scene_type == 'transition':
                # Для переходов - fade через black
                transition_duration = self.transitions['fade_through_black']
            elif scene_type == 'hook' or scene_type == 'cta':
                # Для важных моментов - быстрый crossfade
                transition_duration = self.transitions['crossfade']
            else:
                # Обычный crossfade
                transition_duration = self.transitions['crossfade_slow']

            # Добавляем fade in/out
            if i == 0:
                # Первый клип - только fade in
                clip = clip.fadein(transition_duration)
            elif i == len(clips) - 1:
                # Последний клип - только fade out
                clip = clip.fadeout(transition_duration)
            else:
                # Средние клипы - оба эффекта
                clip = clip.fadein(transition_duration / 2).fadeout(transition_duration / 2)

            transition_clips.append(clip)

        return transition_clips

    def _add_subtitles(
        self,
        video: VideoClip,
        text: str,
        style_name: str,
        duration: float
    ) -> CompositeVideoClip:
        """Добавляет субтитры к видео"""

        # Генерируем субтитры
        srt_content, style_config = self.subtitle_gen.generate_subtitles(
            text,
            duration,
            style_name
        )

        # Создаём subtitle клипы (упрощённая версия)
        # В production версии нужно парсить SRT и создавать TextClip для каждой строки

        subtitle_clip = TextClip(
            text[:100] + "...",  # Демо: показываем начало
            fontsize=style_config.get('fontsize', 60),
            color=style_config.get('color', 'white'),
            font=style_config.get('font', 'Arial-Bold'),
            stroke_color=style_config.get('stroke_color'),
            stroke_width=style_config.get('stroke_width', 2),
            method='caption',
            size=(self.resolution[0] - 200, None),
            align='center'
        ).set_position(('center', 'bottom')).set_duration(duration)

        # Комбинируем
        return CompositeVideoClip([video, subtitle_clip])
