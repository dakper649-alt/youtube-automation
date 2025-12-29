"""
Справочник стоимости YouTube API операций

Источник: https://developers.google.com/youtube/v3/determine_quota_cost
"""

# Стоимость операций YouTube Data API v3 в единицах квоты
API_COSTS = {
    # Чтение данных
    'channels.list': 1,
    'videos.list': 1,
    'playlistItems.list': 1,
    'playlists.list': 1,
    'comments.list': 1,
    'commentThreads.list': 1,

    # Поиск (очень дорого!)
    'search.list': 100,

    # Запись данных
    'videos.insert': 1600,
    'playlists.insert': 50,
    'playlistItems.insert': 50,

    # Обновление
    'videos.update': 50,
    'playlists.update': 50,

    # Удаление
    'videos.delete': 50,
    'playlists.delete': 50,
}


def get_operation_cost(operation: str) -> int:
    """
    Получить стоимость операции

    Args:
        operation: Название операции

    Returns:
        int: Стоимость в единицах квоты
    """
    return API_COSTS.get(operation, 1)  # По умолчанию 1 единица


def estimate_channel_analysis_cost(
    include_videos: int = 20,
    include_similar: int = 5,
    include_search: bool = False
) -> dict:
    """
    Оценка стоимости анализа канала

    Args:
        include_videos: Количество видео для анализа
        include_similar: Количество похожих каналов
        include_search: Включать ли поиск

    Returns:
        dict: Разбивка стоимости
    """
    costs = {
        'channel_info': 1,  # channels.list
        'playlist_items': 1,  # playlistItems.list
        'videos_stats': 1,  # videos.list (батчинг до 50 видео)
        'total': 0
    }

    if include_similar > 0:
        costs['search_similar'] = 100  # search.list
        costs['similar_channels_info'] = include_similar  # channels.list * N

    if include_search:
        costs['topic_search'] = 100  # search.list

    costs['total'] = sum(v for k, v in costs.items() if k != 'total')

    return costs


def daily_quota_budget(daily_limit: int = 10000) -> dict:
    """
    Рекомендованный бюджет квоты на день

    Args:
        daily_limit: Дневной лимит (по умолчанию 10,000)

    Returns:
        dict: Распределение бюджета
    """
    return {
        'daily_limit': daily_limit,
        'reserved_buffer': int(daily_limit * 0.2),  # 20% резерв
        'available_for_operations': int(daily_limit * 0.8),
        'recommended_per_channel': {
            '3_channels': int(daily_limit * 0.8 / 3),  # ~2,666 на канал
            '5_channels': int(daily_limit * 0.8 / 5),  # ~1,600 на канал
            '10_channels': int(daily_limit * 0.8 / 10),  # ~800 на канал
        },
        'max_searches_per_day': int(daily_limit * 0.3 / 100),  # Максимум 30 поисковых запросов
    }
