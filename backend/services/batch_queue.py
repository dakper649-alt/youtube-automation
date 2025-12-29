"""
Batch Queue System - система очередей для массовой генерации видео
Выбираешь 10 видео → уходишь спать → утром всё готово!
"""

import asyncio
import json
import os
from datetime import datetime
from typing import List, Dict, Callable, Optional
from enum import Enum


class VideoStatus(Enum):
    PENDING = "pending"
    GENERATING_SCRIPT = "generating_script"
    GENERATING_IMAGES = "generating_images"
    GENERATING_AUDIO = "generating_audio"
    EDITING_VIDEO = "editing_video"
    COMPLETED = "completed"
    FAILED = "failed"


class BatchQueue:
    """Менеджер очереди видео"""

    def __init__(self, orchestrator):
        self.orchestrator = orchestrator
        self.queue_file = ".batch_queue.json"
        self.queue = self._load_queue()

    def _load_queue(self) -> List[Dict]:
        """Загружает очередь из файла"""
        if os.path.exists(self.queue_file):
            try:
                with open(self.queue_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return []
        return []

    def _save_queue(self):
        """Сохраняет очередь в файл"""
        with open(self.queue_file, 'w', encoding='utf-8') as f:
            json.dump(self.queue, f, indent=2, ensure_ascii=False)

    def add_video_to_queue(
        self,
        niche: str,
        topic: str,
        style: str,
        voice: str,
        subtitle_style: str = "highlighted_words"
    ) -> str:
        """Добавляет видео в очередь"""

        video_id = f"video_{len(self.queue) + 1}_{int(datetime.now().timestamp())}"

        video_task = {
            'id': video_id,
            'niche': niche,
            'topic': topic,
            'style': style,
            'voice': voice,
            'subtitle_style': subtitle_style,
            'status': VideoStatus.PENDING.value,
            'created_at': datetime.now().isoformat(),
            'started_at': None,
            'completed_at': None,
            'error': None,
            'output_path': None
        }

        self.queue.append(video_task)
        self._save_queue()

        print(f"✅ Видео добавлено в очередь: {video_id}")
        print(f"   Тема: {topic}")
        print(f"   Стиль: {style}")
        print(f"   Голос: {voice}")

        return video_id

    def add_batch(self, videos: List[Dict]) -> List[str]:
        """Добавляет несколько видео сразу"""
        video_ids = []

        print(f"\n📦 Добавление {len(videos)} видео в очередь...")

        for video_config in videos:
            video_id = self.add_video_to_queue(**video_config)
            video_ids.append(video_id)

        print(f"\n✅ Добавлено {len(video_ids)} видео в очередь!")
        print(f"🚀 Запусти обработку: python backend/process_queue.py")

        return video_ids

    async def process_queue(self, parallel_workers: int = 1):
        """
        Обрабатывает всю очередь

        Args:
            parallel_workers: Количество одновременных воркеров (по умолчанию 1)
        """

        pending_videos = [v for v in self.queue if v['status'] == VideoStatus.PENDING.value]

        if not pending_videos:
            print("✅ Очередь пуста!")
            return

        print(f"\n🚀 ЗАПУСК ОБРАБОТКИ ОЧЕРЕДИ")
        print(f"=" * 80)
        print(f"📊 Видео в очереди: {len(pending_videos)}")
        print(f"👷 Воркеров: {parallel_workers}")
        print(f"=" * 80)

        # Создаём воркеры
        tasks = []
        for i in range(parallel_workers):
            task = asyncio.create_task(self._worker(i + 1))
            tasks.append(task)

        # Ждём завершения всех воркеров
        await asyncio.gather(*tasks)

        # Финальная статистика
        self._print_final_stats()

    async def _worker(self, worker_id: int):
        """Воркер для обработки видео"""

        while True:
            # Находим следующее видео
            video_task = self._get_next_pending_video()

            if not video_task:
                print(f"[Воркер {worker_id}] Нет больше видео в очереди")
                break

            print(f"\n[Воркер {worker_id}] 🎬 Начинаю обработку: {video_task['id']}")
            print(f"   Тема: {video_task['topic']}")

            video_task['status'] = VideoStatus.GENERATING_SCRIPT.value
            video_task['started_at'] = datetime.now().isoformat()
            self._save_queue()

            try:
                # Генерируем видео через оркестратор
                output_path = await self.orchestrator.create_full_video(
                    topic=video_task['topic'],
                    niche=video_task['niche'],
                    style=video_task['style'],
                    voice=video_task['voice'],
                    subtitle_style=video_task['subtitle_style'],
                    on_progress=lambda status: self._update_video_status(video_task['id'], status)
                )

                # Успешно завершено
                video_task['status'] = VideoStatus.COMPLETED.value
                video_task['completed_at'] = datetime.now().isoformat()
                video_task['output_path'] = output_path
                self._save_queue()

                print(f"\n[Воркер {worker_id}] ✅ Видео готово: {output_path}")

            except Exception as e:
                # Ошибка
                video_task['status'] = VideoStatus.FAILED.value
                video_task['error'] = str(e)
                video_task['completed_at'] = datetime.now().isoformat()
                self._save_queue()

                print(f"\n[Воркер {worker_id}] ❌ Ошибка: {e}")

    def _get_next_pending_video(self) -> Optional[Dict]:
        """Находит следующее видео для обработки"""
        for video in self.queue:
            if video['status'] == VideoStatus.PENDING.value:
                return video
        return None

    def _update_video_status(self, video_id: str, status: str):
        """Обновляет статус видео"""
        for video in self.queue:
            if video['id'] == video_id:
                video['status'] = status
                self._save_queue()
                break

    def _print_final_stats(self):
        """Печатает финальную статистику"""
        completed = len([v for v in self.queue if v['status'] == VideoStatus.COMPLETED.value])
        failed = len([v for v in self.queue if v['status'] == VideoStatus.FAILED.value])

        print(f"\n" + "=" * 80)
        print(f"🎉 ОБРАБОТКА ОЧЕРЕДИ ЗАВЕРШЕНА!")
        print(f"=" * 80)
        print(f"✅ Успешно: {completed}")
        print(f"❌ Ошибок: {failed}")
        print(f"=" * 80)

        if completed > 0:
            print(f"\n📁 Готовые видео:")
            for video in self.queue:
                if video['status'] == VideoStatus.COMPLETED.value:
                    print(f"   ✅ {video['topic']}")
                    print(f"      📄 {video['output_path']}")

        if failed > 0:
            print(f"\n❌ Видео с ошибками:")
            for video in self.queue:
                if video['status'] == VideoStatus.FAILED.value:
                    print(f"   ❌ {video['topic']}")
                    print(f"      Ошибка: {video['error']}")

    def get_queue_status(self) -> Dict:
        """Возвращает статус очереди"""
        return {
            'total': len(self.queue),
            'pending': len([v for v in self.queue if v['status'] == VideoStatus.PENDING.value]),
            'in_progress': len([v for v in self.queue if v['status'] not in [VideoStatus.PENDING.value, VideoStatus.COMPLETED.value, VideoStatus.FAILED.value]]),
            'completed': len([v for v in self.queue if v['status'] == VideoStatus.COMPLETED.value]),
            'failed': len([v for v in self.queue if v['status'] == VideoStatus.FAILED.value])
        }

    def clear_completed(self):
        """Удаляет завершённые видео из очереди"""
        self.queue = [v for v in self.queue if v['status'] != VideoStatus.COMPLETED.value]
        self._save_queue()
        print("✅ Завершённые видео удалены из очереди")

    def clear_all(self):
        """Очищает всю очередь"""
        self.queue = []
        self._save_queue()
        print("✅ Очередь полностью очищена")

    def retry_failed(self):
        """Повторяет обработку ошибочных видео"""
        failed_count = 0
        for video in self.queue:
            if video['status'] == VideoStatus.FAILED.value:
                video['status'] = VideoStatus.PENDING.value
                video['error'] = None
                failed_count += 1

        self._save_queue()
        print(f"✅ {failed_count} видео помечено для повторной обработки")
