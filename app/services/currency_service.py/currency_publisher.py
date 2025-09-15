from app.core.config import settings
from app.core.logger_config import get_logger
from app.rabbitMQ.publisher import RabbitPublisher


logger = get_logger(__name__)


class CurrencyPublisher:
    def __init__(self):
        self.publisher = RabbitPublisher(rabbit_url=settings.RABBIT_URL)

    async def publish_currency_rates(self, currency_data: dict):

        # Отправляем данные в Rabbit

        try:
            success = await self.publisher.publish_to_exchange(
                exchange_name="currency_exchange",
                exchange_type="direct",
                routing_key="currency.rates",
                message_body=currency_data,
                content_type="application/json",
            )

            return success

        except Exception as e:
            logger.error(f"Произошла ошибка отправки данных в rabbitMQ: {e}")
