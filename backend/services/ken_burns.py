"""
Ken Burns Effects - профессиональные эффекты движения камеры
Умная логика: хук → zoom in, переходы → pan, CTA → zoom in
"""

from enum import Enum
from typing import Dict, List, Optional, Tuple
import random


class EffectType(Enum):
    """Типы эффектов Ken Burns"""
    ZOOM_IN = "zoom_in"           # Приближение - для важных моментов
    ZOOM_OUT = "zoom_out"         # Отдаление - для обзора
    PAN_LEFT = "pan_left"         # Панорама влево
    PAN_RIGHT = "pan_right"       # Панорама вправо
    PAN_UP = "pan_up"             # Панорама вверх
    PAN_DOWN = "pan_down"         # Панорама вниз
    ZOOM_PAN = "zoom_pan"         # Комбо: зум + панорама
    STATIC = "static"             # Без движения - для текста


class SceneType(Enum):
    """Типы сцен в видео"""
    HOOK = "hook"                 # Хук - первые 3-10 секунд
    INTRODUCTION = "introduction"  # Вступление
    MAIN_POINT = "main_point"     # Основная мысль
    EXAMPLE = "example"           # Пример
    TRANSITION = "transition"     # Переход между темами
    EMPHASIS = "emphasis"         # Акцент/важность
    CTA = "cta"                   # Call to Action
    CONCLUSION = "conclusion"     # Заключение
    REGULAR = "regular"           # Обычная сцена


class KenBurnsEffect:
    """
    Менеджер эффектов Ken Burns с умной логикой

    Автоматически выбирает эффект на основе:
    - Типа сцены (хук, переход, CTA и т.д.)
    - Позиции в видео (начало, середина, конец)
    - Содержания текста (ключевые слова)
    """

    def __init__(self):
        # Паттерны для определения типов сцен
        self.scene_patterns = {
            SceneType.HOOK: [
                'знаете ли вы', 'представьте', 'что если', 'секрет',
                'никто не знает', 'шокирующая правда', 'удивительно'
            ],
            SceneType.TRANSITION: [
                'но', 'однако', 'теперь', 'далее', 'перейдём',
                'следующий', 'также', 'кроме того', 'более того'
            ],
            SceneType.EXAMPLE: [
                'например', 'к примеру', 'допустим', 'представим',
                'случай', 'история', 'пример'
            ],
            SceneType.EMPHASIS: [
                'важно', 'ключевой', 'главное', 'критично',
                'необходимо', 'обязательно', 'помните'
            ],
            SceneType.CTA: [
                'подпишитесь', 'лайк', 'комментарий', 'поделитесь',
                'нажмите', 'оставьте', 'напишите', 'канал'
            ],
            SceneType.CONCLUSION: [
                'итак', 'в заключение', 'подводя итог', 'резюмируя',
                'в итоге', 'таким образом', 'следовательно'
            ]
        }

        # Правила выбора эффектов для каждого типа сцены
        self.effect_rules = {
            SceneType.HOOK: [
                (EffectType.ZOOM_IN, 0.5),      # 50% - драматичное приближение
                (EffectType.ZOOM_PAN, 0.3),      # 30% - комбо для wow-эффекта
                (EffectType.PAN_RIGHT, 0.2)      # 20% - движение для динамики
            ],
            SceneType.INTRODUCTION: [
                (EffectType.ZOOM_OUT, 0.4),      # 40% - показать общую картину
                (EffectType.PAN_LEFT, 0.3),      # 30% - плавное введение
                (EffectType.STATIC, 0.3)         # 30% - фокус на тексте
            ],
            SceneType.MAIN_POINT: [
                (EffectType.ZOOM_IN, 0.5),       # 50% - фокус на важном
                (EffectType.STATIC, 0.3),        # 30% - без отвлечения
                (EffectType.ZOOM_PAN, 0.2)       # 20% - динамика
            ],
            SceneType.EXAMPLE: [
                (EffectType.PAN_RIGHT, 0.35),    # 35% - показываем детали
                (EffectType.PAN_LEFT, 0.35),     # 35% - альтернатива
                (EffectType.ZOOM_OUT, 0.3)       # 30% - общий план
            ],
            SceneType.TRANSITION: [
                (EffectType.PAN_LEFT, 0.4),      # 40% - переход
                (EffectType.PAN_RIGHT, 0.4),     # 40% - альтернатива
                (EffectType.ZOOM_OUT, 0.2)       # 20% - смена контекста
            ],
            SceneType.EMPHASIS: [
                (EffectType.ZOOM_IN, 0.7),       # 70% - ВНИМАНИЕ!
                (EffectType.ZOOM_PAN, 0.2),      # 20% - драма
                (EffectType.STATIC, 0.1)         # 10% - пауза
            ],
            SceneType.CTA: [
                (EffectType.ZOOM_IN, 0.6),       # 60% - призыв к действию
                (EffectType.STATIC, 0.3),        # 30% - читабельность
                (EffectType.ZOOM_PAN, 0.1)       # 10% - активность
            ],
            SceneType.CONCLUSION: [
                (EffectType.ZOOM_OUT, 0.5),      # 50% - общая картина
                (EffectType.STATIC, 0.3),        # 30% - подведение итогов
                (EffectType.PAN_UP, 0.2)         # 20% - подъём
            ],
            SceneType.REGULAR: [
                (EffectType.PAN_RIGHT, 0.25),    # 25% - базовое движение
                (EffectType.PAN_LEFT, 0.25),     # 25% - альтернатива
                (EffectType.ZOOM_IN, 0.2),       # 20% - лёгкий зум
                (EffectType.ZOOM_OUT, 0.15),     # 15% - отдаление
                (EffectType.STATIC, 0.15)        # 15% - спокойствие
            ]
        }

        # Параметры эффектов (начальный и конечный масштаб/позиция)
        self.effect_params = {
            EffectType.ZOOM_IN: {
                'start_scale': 1.0,
                'end_scale': 1.3,
                'start_position': (0.5, 0.5),
                'end_position': (0.5, 0.5)
            },
            EffectType.ZOOM_OUT: {
                'start_scale': 1.3,
                'end_scale': 1.0,
                'start_position': (0.5, 0.5),
                'end_position': (0.5, 0.5)
            },
            EffectType.PAN_LEFT: {
                'start_scale': 1.2,
                'end_scale': 1.2,
                'start_position': (0.6, 0.5),
                'end_position': (0.4, 0.5)
            },
            EffectType.PAN_RIGHT: {
                'start_scale': 1.2,
                'end_scale': 1.2,
                'start_position': (0.4, 0.5),
                'end_position': (0.6, 0.5)
            },
            EffectType.PAN_UP: {
                'start_scale': 1.2,
                'end_scale': 1.2,
                'start_position': (0.5, 0.6),
                'end_position': (0.5, 0.4)
            },
            EffectType.PAN_DOWN: {
                'start_scale': 1.2,
                'end_scale': 1.2,
                'start_position': (0.5, 0.4),
                'end_position': (0.5, 0.6)
            },
            EffectType.ZOOM_PAN: {
                'start_scale': 1.0,
                'end_scale': 1.4,
                'start_position': (0.4, 0.4),
                'end_position': (0.6, 0.6)
            },
            EffectType.STATIC: {
                'start_scale': 1.0,
                'end_scale': 1.0,
                'start_position': (0.5, 0.5),
                'end_position': (0.5, 0.5)
            }
        }

        # Статистика использования
        self.stats = {
            'total_scenes': 0,
            'effects_used': {},
            'scene_types_detected': {}
        }

    def detect_scene_type(
        self,
        scene_index: int,
        total_scenes: int,
        scene_text: str,
        script_metadata: Optional[Dict] = None
    ) -> SceneType:
        """
        Определяет тип сцены на основе позиции и содержания

        Args:
            scene_index: Индекс сцены (начиная с 0)
            total_scenes: Общее количество сцен
            scene_text: Текст сцены
            script_metadata: Дополнительные метаданные скрипта

        Returns:
            Тип сцены (SceneType)
        """

        # Позиция сцены в видео (0.0 - начало, 1.0 - конец)
        position = scene_index / max(total_scenes - 1, 1)

        text_lower = scene_text.lower()

        # HOOK - первые 10-15% видео
        if position < 0.15:
            return SceneType.HOOK

        # CONCLUSION - последние 10-15% видео
        if position > 0.85:
            return SceneType.CONCLUSION

        # Проверяем паттерны по ключевым словам
        for scene_type, keywords in self.scene_patterns.items():
            if any(keyword in text_lower for keyword in keywords):
                return scene_type

        # INTRODUCTION - первая треть видео
        if position < 0.33:
            return SceneType.INTRODUCTION

        # MAIN_POINT - средняя часть
        if 0.33 <= position <= 0.66:
            return SceneType.MAIN_POINT

        # По умолчанию - обычная сцена
        return SceneType.REGULAR

    def select_effect(
        self,
        scene_type: SceneType,
        previous_effect: Optional[EffectType] = None
    ) -> EffectType:
        """
        Выбирает эффект на основе типа сцены

        Args:
            scene_type: Тип сцены
            previous_effect: Предыдущий эффект (для разнообразия)

        Returns:
            Выбранный эффект (EffectType)
        """

        # Получаем правила для данного типа сцены
        rules = self.effect_rules.get(scene_type, self.effect_rules[SceneType.REGULAR])

        # Фильтруем, чтобы не повторять предыдущий эффект (если возможно)
        if previous_effect:
            available_rules = [(effect, prob) for effect, prob in rules if effect != previous_effect]
            if available_rules:
                # Пересчитываем вероятности
                total_prob = sum(prob for _, prob in available_rules)
                rules = [(effect, prob / total_prob) for effect, prob in available_rules]

        # Выбираем эффект на основе вероятностей
        effects = [effect for effect, _ in rules]
        probabilities = [prob for _, prob in rules]

        selected_effect = random.choices(effects, weights=probabilities, k=1)[0]

        # Обновляем статистику
        self.stats['effects_used'][selected_effect.value] = \
            self.stats['effects_used'].get(selected_effect.value, 0) + 1

        return selected_effect

    def get_effect_params(self, effect_type: EffectType) -> Dict:
        """
        Возвращает параметры эффекта

        Args:
            effect_type: Тип эффекта

        Returns:
            Словарь с параметрами (масштаб, позиция)
        """
        return self.effect_params[effect_type].copy()

    def process_scenes(
        self,
        scenes: List[Dict],
        script_metadata: Optional[Dict] = None
    ) -> List[Dict]:
        """
        Обрабатывает все сцены и назначает эффекты

        Args:
            scenes: Список сцен [{'text': '...', 'duration': 5.0}, ...]
            script_metadata: Метаданные скрипта

        Returns:
            Список сцен с назначенными эффектами
        """

        total_scenes = len(scenes)
        previous_effect = None

        enriched_scenes = []

        for i, scene in enumerate(scenes):
            # Определяем тип сцены
            scene_type = self.detect_scene_type(
                scene_index=i,
                total_scenes=total_scenes,
                scene_text=scene.get('text', ''),
                script_metadata=script_metadata
            )

            # Выбираем эффект
            effect_type = self.select_effect(scene_type, previous_effect)

            # Получаем параметры эффекта
            effect_params = self.get_effect_params(effect_type)

            # Обогащаем сцену
            enriched_scene = scene.copy()
            enriched_scene.update({
                'scene_type': scene_type.value,
                'effect_type': effect_type.value,
                'effect_params': effect_params
            })

            enriched_scenes.append(enriched_scene)

            # Обновляем статистику
            self.stats['total_scenes'] += 1
            self.stats['scene_types_detected'][scene_type.value] = \
                self.stats['scene_types_detected'].get(scene_type.value, 0) + 1

            previous_effect = effect_type

        return enriched_scenes

    def get_stats(self) -> Dict:
        """Возвращает статистику использования"""
        return {
            'total_scenes': self.stats['total_scenes'],
            'effects_distribution': self.stats['effects_used'],
            'scene_types_distribution': self.stats['scene_types_detected']
        }

    def reset_stats(self):
        """Сбрасывает статистику"""
        self.stats = {
            'total_scenes': 0,
            'effects_used': {},
            'scene_types_detected': {}
        }
