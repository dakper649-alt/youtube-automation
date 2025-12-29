#!/usr/bin/env python3
"""
Мониторинг здоровья API ключей

Использование:
    python backend/check_keys_health.py

Показывает:
    - Количество активных/заблокированных/ожидающих ключей
    - Детали waiting_list
    - Рекомендации по добавлению новых ключей
"""

import sys
import os
from datetime import datetime

# Добавляем путь к модулям
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from backend.services.api_key_manager import SafeAPIManager


def main():
    """Главная функция мониторинга"""

    print("=" * 80)
    print("🏥 МОНИТОРИНГ ЗДОРОВЬЯ API КЛЮЧЕЙ")
    print("=" * 80)

    try:
        manager = SafeAPIManager()
    except Exception as e:
        print(f"❌ Ошибка инициализации менеджера: {e}")
        return

    report = manager.get_health_report()

    # YouTube
    print("\n📺 YOUTUBE DATA API:")
    print(f"   ✅ Активных: {report['youtube']['active']}/{report['youtube']['total']}")
    print(f"   ⏳ В ожидании: {report['youtube']['waiting']}")
    print(f"   🚫 Заблокировано: {report['youtube']['blocked']}")

    # ElevenLabs
    print("\n🎙️  ELEVENLABS API:")
    print(f"   ✅ Активных: {report['elevenlabs']['active']}/{report['elevenlabs']['total']}")
    print(f"   ⏳ В ожидании: {report['elevenlabs']['waiting']}")
    print(f"   🚫 Заблокировано: {report['elevenlabs']['blocked']}")

    # Детали ожидания
    if report['waiting_list_details']:
        print("\n⏳ КЛЮЧИ В ОЖИДАНИИ:")
        for item in report['waiting_list_details']:
            release_time = datetime.fromisoformat(item['release_at'])
            service_emoji = "📺" if item['service'] == 'youtube' else "🎙️"
            print(f"   {service_emoji} {item['service'].upper()}: {item['key_hash']} → освободится {release_time.strftime('%d.%m.%Y %H:%M')}")

    # Заблокированные ключи
    if report['blocked_keys']:
        print("\n🚫 ЗАБЛОКИРОВАННЫЕ КЛЮЧИ (навсегда):")
        for item in report['blocked_keys']:
            service_emoji = "📺" if item['service'] == 'youtube' else "🎙️"
            print(f"   {service_emoji} {item['service'].upper()}: {item['key_hash']}")

    print("\n" + "=" * 80)

    # Рекомендации
    print("\n💡 РЕКОМЕНДАЦИИ:")

    recommendations = []

    if report['youtube']['total'] == 0:
        recommendations.append("   ⚠️  НЕТ YouTube ключей! Добавьте в .env: YOUTUBE_API_KEY_1=your_key")
    elif report['youtube']['active'] < 3:
        recommendations.append("   ⚠️  Мало активных YouTube ключей! Рекомендуем минимум 3.")

    if report['elevenlabs']['total'] == 0:
        recommendations.append("   ⚠️  НЕТ ElevenLabs ключей! Добавьте в .env: ELEVENLABS_API_KEY_1=your_key")
    elif report['elevenlabs']['active'] < 3:
        recommendations.append("   ⚠️  Мало активных ElevenLabs ключей! Рекомендуем минимум 5.")

    if report['youtube']['blocked'] > 0:
        recommendations.append(f"   🚫 {report['youtube']['blocked']} YouTube ключей заблокировано! Создайте новые.")

    if report['elevenlabs']['blocked'] > 0:
        recommendations.append(f"   🚫 {report['elevenlabs']['blocked']} ElevenLabs ключей заблокировано! Создайте новые.")

    if not recommendations:
        print("   ✅ Всё в порядке! Ключей достаточно для стабильной работы.")
    else:
        for rec in recommendations:
            print(rec)

    print("\n" + "=" * 80)
    print("\n📊 СТАТИСТИКА ИСПОЛЬЗОВАНИЯ:")
    print("   Проверьте файл: .api_keys_status.json")
    print("   Кэш использования: .api_keys_cache.json")
    print("\n" + "=" * 80)


if __name__ == "__main__":
    main()
