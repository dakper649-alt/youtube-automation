"""
Генератор изображений через Hugging Face Stable Diffusion FLUX
Поддержка 20 стилей, consistent персонажей, Reference Image
"""

import os
import asyncio
import requests
import io
from PIL import Image
from typing import Dict, List, Optional
import hashlib
import json

# Import image styles configuration
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from config.image_styles import get_style_prompt, IMAGE_STYLES, validate_style


class ImageGenerator:
    """Генератор изображений с поддержкой 20 стилей"""

    def __init__(self, api_key_manager):
        self.key_manager = api_key_manager

        # Hugging Face API endpoint
        self.api_url = "https://api-inference.huggingface.co/models/black-forest-labs/FLUX.1-schnell"

        # Кэш для reference изображений персонажей
        self.character_cache = {}

        # 20 стилей изображений из конфига
        self.styles = IMAGE_STYLES
        print(f"✅ ImageGenerator инициализирован с {len(self.styles)} стилями")

    def _init_styles_OLD_DEPRECATED(self) -> Dict:
        """Инициализация всех 20 стилей"""
        return {
            # ═══════════════════════════════════════════════════════════
            # MINIMALISM (4 стиля)
            # ═══════════════════════════════════════════════════════════
            "minimalist_stick_figure": {
                "name": "Minimalist Stick Figure",
                "base_prompt": "simple stick figure illustration, minimalist line art, {scene}, white background, black outlines, educational diagram style, clean composition, 2D flat design",
                "negative_prompt": "realistic, detailed, photo, 3D, shadows, complex, colorful",
                "best_for": ["psychology", "education", "concepts", "explanations"],
                "character_support": True
            },

            "flat_design_icons": {
                "name": "Flat Design Icons",
                "base_prompt": "flat design illustration, {scene}, simple geometric shapes, bright solid colors, modern minimalist style, vector art aesthetic, no shadows, 2D",
                "negative_prompt": "realistic, 3D, gradients, textures, photo",
                "best_for": ["business", "tech", "startups", "apps"],
                "character_support": True
            },

            "line_art_portraits": {
                "name": "Line Art Portraits",
                "base_prompt": "continuous line art, {scene}, single line drawing, minimalist portrait style, elegant linework, white background, artistic sketch",
                "negative_prompt": "colored, filled, shaded, photo, realistic",
                "best_for": ["stories", "biographies", "interviews", "podcasts"],
                "character_support": True
            },

            "geometric_minimalism": {
                "name": "Geometric Minimalism",
                "base_prompt": "geometric abstract art, {scene}, simple shapes, triangles circles squares, minimalist composition, limited color palette, modern design",
                "negative_prompt": "realistic, detailed, organic, photo",
                "best_for": ["design", "architecture", "modern art", "tech"],
                "character_support": False
            },

            # ═══════════════════════════════════════════════════════════
            # REALISM (4 стиля)
            # ═══════════════════════════════════════════════════════════
            "cinematic_photography": {
                "name": "Cinematic Photography",
                "base_prompt": "cinematic photography, {scene}, dramatic lighting, film grain, professional color grading, bokeh background, shallow depth of field, movie still aesthetic, high detail",
                "negative_prompt": "cartoon, illustration, drawing, sketch, unrealistic",
                "best_for": ["stories", "documentary", "drama", "emotional"],
                "character_support": True
            },

            "photorealistic_portrait": {
                "name": "Photorealistic Portrait",
                "base_prompt": "photorealistic portrait, {scene}, studio lighting, sharp focus, detailed skin texture, professional photography, DSLR quality, 85mm lens",
                "negative_prompt": "illustration, cartoon, painting, sketch",
                "best_for": ["biographies", "interviews", "personal stories"],
                "character_support": True
            },

            "documentary_style": {
                "name": "Documentary Style",
                "base_prompt": "documentary photography, {scene}, natural lighting, candid moment, journalistic style, authentic atmosphere, real-life scene",
                "negative_prompt": "staged, artificial, cartoon, illustration",
                "best_for": ["news", "investigations", "real events"],
                "character_support": True
            },

            "street_photography": {
                "name": "Street Photography",
                "base_prompt": "street photography, {scene}, urban environment, candid capture, natural lighting, authentic moment, photojournalism style",
                "negative_prompt": "studio, staged, illustration, cartoon",
                "best_for": ["urban stories", "social topics", "lifestyle"],
                "character_support": True
            },

            # ═══════════════════════════════════════════════════════════
            # ILLUSTRATIONS (4 стиля)
            # ═══════════════════════════════════════════════════════════
            "digital_painting": {
                "name": "Digital Painting",
                "base_prompt": "digital painting, {scene}, painterly style, rich colors, detailed illustration, concept art quality, brush strokes visible, artistic rendering",
                "negative_prompt": "photo, 3D render, low quality, blurry",
                "best_for": ["fantasy", "adventures", "creative stories"],
                "character_support": True
            },

            "watercolor_art": {
                "name": "Watercolor Art",
                "base_prompt": "watercolor painting, {scene}, soft colors, flowing pigments, artistic texture, hand-painted feel, delicate details, paper texture",
                "negative_prompt": "digital, photo, sharp edges, 3D",
                "best_for": ["poetry", "nature", "gentle stories", "art"],
                "character_support": True
            },

            "comic_book_style": {
                "name": "Comic Book Style",
                "base_prompt": "comic book illustration, {scene}, bold outlines, vibrant colors, halftone dots, pop art style, dynamic composition, graphic novel aesthetic",
                "negative_prompt": "realistic, photo, 3D, muted colors",
                "best_for": ["action", "superheroes", "adventures", "fun"],
                "character_support": True
            },

            "cute_kawaii_characters": {
                "name": "Cute Kawaii Characters",
                "base_prompt": "kawaii style illustration, {scene}, cute characters, big eyes, chibi proportions, pastel colors, adorable aesthetic, manga influence",
                "negative_prompt": "realistic, scary, dark, detailed",
                "best_for": ["positive content", "children", "fun", "uplifting"],
                "character_support": True
            },

            # ═══════════════════════════════════════════════════════════
            # NICHE-SPECIFIC (4 стиля)
            # ═══════════════════════════════════════════════════════════
            "military_documentary": {
                "name": "Military Documentary",
                "base_prompt": "military documentary photography, {scene}, tactical realism, authentic equipment, professional documentation, historical accuracy, serious tone",
                "negative_prompt": "cartoon, fantasy, unrealistic, colorful",
                "best_for": ["war history", "military", "veterans"],
                "character_support": True
            },

            "war_sketch_art": {
                "name": "War Sketch Art",
                "base_prompt": "war sketch art, {scene}, pencil drawing style, historical illustration, battlefield sketch, dramatic shading, documentary art style",
                "negative_prompt": "colorful, modern, photo, cartoon",
                "best_for": ["military memoirs", "historical stories"],
                "character_support": True
            },

            "scifi_futuristic": {
                "name": "Sci-Fi Futuristic",
                "base_prompt": "sci-fi futuristic scene, {scene}, high-tech environment, neon lights, cyberpunk aesthetic, advanced technology, holographic displays, sleek design",
                "negative_prompt": "medieval, natural, vintage, low-tech",
                "best_for": ["technology", "AI", "future", "innovation"],
                "character_support": True
            },

            "horror_dark_aesthetic": {
                "name": "Horror Dark Aesthetic",
                "base_prompt": "dark horror aesthetic, {scene}, ominous atmosphere, dramatic shadows, moody lighting, eerie environment, suspenseful mood, cinematic darkness",
                "negative_prompt": "bright, cheerful, colorful, cute",
                "best_for": ["scary stories", "horror", "mystery", "thriller"],
                "character_support": True
            },

            # ═══════════════════════════════════════════════════════════
            # CORPORATE/BUSINESS (4 стиля)
            # ═══════════════════════════════════════════════════════════
            "corporate_infographic": {
                "name": "Corporate Infographic",
                "base_prompt": "corporate infographic style, {scene}, clean professional design, business graphics, charts and diagrams, modern layout, blue and white color scheme",
                "negative_prompt": "messy, hand-drawn, artistic, colorful",
                "best_for": ["business", "finance", "statistics", "reports"],
                "character_support": False
            },

            "isometric_illustration": {
                "name": "Isometric Illustration",
                "base_prompt": "isometric illustration, {scene}, 3D perspective, geometric precision, tech startup aesthetic, modern clean design, professional look",
                "negative_prompt": "realistic, photo, 2D flat, messy",
                "best_for": ["tech processes", "workflows", "systems"],
                "character_support": False
            },

            "data_visualization": {
                "name": "Data Visualization",
                "base_prompt": "data visualization design, {scene}, charts graphs infographics, modern professional style, clean layout, information design, analytical aesthetic",
                "negative_prompt": "artistic, messy, hand-drawn, decorative",
                "best_for": ["statistics", "research", "analytics", "science"],
                "character_support": False
            },

            "retro_vintage": {
                "name": "Retro Vintage",
                "base_prompt": "retro vintage style, {scene}, nostalgic aesthetic, faded colors, old photograph feel, vintage design elements, historical atmosphere",
                "negative_prompt": "modern, digital, futuristic, high-tech",
                "best_for": ["history", "nostalgia", "old stories", "classics"],
                "character_support": True
            }
        }

    async def generate_images_for_script(
        self,
        script: str,
        image_prompts: List[Dict],
        style: str,
        output_dir: str
    ) -> List[Dict]:
        """
        Генерирует все изображения для видео

        Args:
            script: Текст скрипта
            image_prompts: Список промптов от ScriptGenerator
            style: Выбранный стиль
            output_dir: Папка для сохранения

        Returns:
            Список путей к сгенерированным изображениям
        """

        os.makedirs(output_dir, exist_ok=True)

        print(f"\n🎨 Генерация {len(image_prompts)} изображений...")

        # Validate and log style
        if not validate_style(style):
            print(f"⚠️ Неизвестный стиль '{style}', использую minimalist_stick_figure")
            style = 'minimalist_stick_figure'

        print(f"📐 Стиль: {self.styles[style]['name']}")
        print(f"   {self.styles[style]['emoji']} {self.styles[style]['description']}")

        # Проверяем нужен ли consistent персонаж (по умолчанию отключаем для упрощения)
        needs_character = False  # Simplified: disable character consistency
        reference_image = None

        # Генерируем все изображения
        results = []
        for i, prompt_data in enumerate(image_prompts, 1):
            print(f"\n[{i}/{len(image_prompts)}] Генерирую сцену...")

            image_path = await self.generate_single_image(
                prompt=prompt_data['prompt'],
                style=style,
                output_path=f"{output_dir}/scene_{i:03d}.png",
                reference_image=reference_image if needs_character else None
            )

            results.append({
                'path': image_path,
                'timestamp': prompt_data['timestamp'],
                'duration': prompt_data['duration'],
                'scene_description': prompt_data['scene_description']
            })

            # Человекоподобная задержка
            await asyncio.sleep(2)

        print(f"\n✅ Все {len(results)} изображений сгенерированы!")
        return results

    def _detect_character_in_script(self, script: str) -> bool:
        """Определяет есть ли персонаж в скрипте"""
        character_indicators = [
            'он ', 'она ', 'его ', 'её ', 'ему ', 'ей ',
            'человек', 'мужчина', 'женщина', 'парень', 'девушка',
            'герой', 'героиня', 'персонаж', 'главный герой'
        ]

        script_lower = script.lower()
        return any(indicator in script_lower for indicator in character_indicators)

    async def _create_reference_character(
        self,
        script: str,
        style: str,
        output_dir: str
    ) -> str:
        """Создаёт reference изображение персонажа"""

        # Извлекаем описание персонажа из скрипта
        character_description = self._extract_character_description(script)

        # Генерируем reference портрет
        style_config = self.styles[style]
        prompt = style_config['base_prompt'].format(
            scene=f"portrait of {character_description}, neutral expression, front view, character reference sheet"
        )

        reference_path = f"{output_dir}/character_reference.png"

        print(f"   Описание персонажа: {character_description[:100]}...")

        await self.generate_single_image(
            prompt=prompt,
            style=style,
            output_path=reference_path
        )

        return reference_path

    def _extract_character_description(self, script: str) -> str:
        """Извлекает описание персонажа из скрипта"""
        # Простая эвристика - можно улучшить через LLM
        words = script.split()[:200]  # Берём начало скрипта

        # Ищем описательные фразы
        description_parts = []

        if 'мужчина' in script.lower():
            description_parts.append('middle-aged man')
        elif 'женщина' in script.lower():
            description_parts.append('middle-aged woman')
        elif 'парень' in script.lower():
            description_parts.append('young man')
        elif 'девушка' in script.lower():
            description_parts.append('young woman')
        else:
            description_parts.append('person')

        description_parts.append('casual clothing, neutral background')

        return ', '.join(description_parts)

    async def generate_single_image(
        self,
        prompt: str,
        style: str,
        output_path: str,
        reference_image: Optional[str] = None
    ) -> str:
        """Генерирует одно изображение"""

        # Используем get_style_prompt из конфига для применения стиля
        full_prompt = get_style_prompt(style, prompt)

        # Добавляем качественные параметры
        full_prompt += ", high quality, detailed, professional, 8k resolution"

        # Получаем API ключ
        api_key = await self.key_manager.get_safe_hf_key()

        headers = {
            "Authorization": f"Bearer {api_key}"
        }

        payload = {
            "inputs": full_prompt,
            "parameters": {
                "negative_prompt": "low quality, blurry, distorted, ugly, bad anatomy",
                "num_inference_steps": 25,
                "guidance_scale": 7.5,
                "width": 1920,  # Больше для Ken Burns
                "height": 1080
            }
        }

        # Если есть reference изображение - добавляем
        if reference_image and os.path.exists(reference_image):
            with open(reference_image, 'rb') as f:
                reference_data = f.read()
            payload['parameters']['init_image'] = reference_data
            payload['parameters']['strength'] = 0.7

        try:
            response = requests.post(
                self.api_url,
                headers=headers,
                json=payload,
                timeout=60
            )

            if response.status_code == 200:
                image = Image.open(io.BytesIO(response.content))
                image.save(output_path)

                # Трекаем использование
                self.key_manager.track_usage('huggingface', api_key, 1)

                print(f"   ✅ Сохранено: {output_path}")
                return output_path
            else:
                print(f"   ❌ Ошибка API: {response.status_code}")
                print(f"   {response.text}")

                # Отмечаем ошибку
                self.key_manager.mark_key_as_blocked(
                    'huggingface',
                    api_key,
                    f"HTTP {response.status_code}"
                )

                # Retry с другим ключом
                return await self.generate_single_image(
                    prompt, style, output_path, reference_image
                )

        except Exception as e:
            print(f"   ❌ Ошибка генерации: {e}")
            raise

    def get_style_recommendations(self, niche: str) -> List[str]:
        """Рекомендует стили для ниши"""
        recommendations = []

        niche_lower = niche.lower()

        for style_id, style_config in self.styles.items():
            # Проверяем подходит ли стиль для ниши
            for category in style_config['best_for']:
                if category in niche_lower:
                    recommendations.append(style_id)
                    break

        # Если ничего не подошло - возвращаем универсальные
        if not recommendations:
            recommendations = [
                'minimalist_stick_figure',
                'digital_painting',
                'cinematic_photography'
            ]

        return recommendations
