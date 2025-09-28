from app.core.logger_config import get_logger

from app.services.currency_service.api_client import CurrencyParser
from app.services.currency_service.currency_cache import CurrencyCache
from app.services.currency_service.currency_publisher import CurrencyPublisher
from app.core.config import settings


logger = get_logger(__name__)


class CurrencyService:
    def __init__(
        self,
    ):
        self.parser = CurrencyParser()
        self.cache = CurrencyCache()
        self.publisher = CurrencyPublisher()

    async def fetch_currency_rates(self):
        try:
            # Подтягиваем данные с АПИшки
            rates_data = await self.parser.extract_currency_data()
            if not rates_data:
                logger.warning("Не удается получить данные с API")
                return None
            return rates_data

        except Exception as e:
            logger.error(f"Произошла ошибка получения данных с API: {e}")
            return None

    async def publish_currency_rates(self, rates_data: dict):
        # Отправляем в брокер
        try:

            success = await self.publisher.publish_currency_rates(rates_data)

            if success:
                logger.info("Данные успешно отправлены в очередь")

            else:
                logger.error("Произошла ошибка передачи данных в RabbitMQ")

            return success

        except Exception as e:
            logger.error(f"Произошла ошибка передачи данных в RabbitMQ: {e}")
            return None

    async def get_cached_rates(self):
        # Только получение данных из кэша

        try:
            cache_data = await self.cache.get_cached_rates()
            if cache_data:
                logger.info("Данные получены из Redis")
                return cache_data

        except Exception as e:
            logger.error(f"Произошла ошибка получения данных из кэша: {e}")

    async def cache_currency_rates(self, rates_data: dict):
        try:
            success_cache = await self.cache.set_cached_rates(rates_data)

            if success_cache:
                logger.info("✅ Данные успешно сохранены в Redis")
            else:
                logger.warning("⚠️ Не удалось сохранить данные в Redis")

            return success_cache

        except Exception as e:
            logger.error(f"❌ Ошибка сохранения в кэш: {e}")
            return False

    async def execute_currency_pipeline(self):
        try:

            rates = await self.fetch_currency_rates()
            if not rates:
                return False

            cache_success = await self.cache_currency_rates(rates_data=rates)

            if not cache_success:
                logger.warning("Данные не сохранены в кэш , но продолжаем")

            publish_success = await self.publish_currency_rates(rates_data=rates)

            return publish_success

        except Exception as e:
            logger.error(f"Произошла ошибка выполнения отправки в RabbitMQ: {e}")
