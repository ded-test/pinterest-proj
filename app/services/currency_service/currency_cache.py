import json
from app.core.logger_config import get_logger
from app.core.database import redis_manager
from datetime import datetime

logger = get_logger(__name__)


class CurrencyCache:
    def __init__(
        self, cache_key: str = "currency_rates:latest", ttl: int = 3600
    ):  # Данные хранятся в кэше 1 час

        self.cache_key = cache_key
        self.ttl = ttl

    async def get_cached_rates(self):
        # Получаем данные из кэша
        try:

            cache_data = await redis_manager.get(self.cache_key)
            if cache_data:
                data = json.loads(cache_data)
                data["from_cache"] = True
                return data
            return None

        except Exception as e:
            logger.error(f"Произошла ошибка получения данных из кэша: {e}")

    async def set_cached_rates(self, data: dict) -> bool:
        try:
            # Делаем копирование оригинальных данных и добавляем в словарь ключ со временем внесения в кэш
            data_to_cache = data.copy()
            data_to_cache["created_at"] = datetime.now().isoformat()

            await redis_manager.set(
                key=self.cache_key, value=json.dumps(data_to_cache), expire=self.ttl
            )
            return True

        except Exception as e:
            logger.error(f"Произошла ошибка установки данных в кэш: {e}")
            return False
