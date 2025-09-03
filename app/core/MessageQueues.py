from app.core.database import rabbit_manager
from app.rabbitMQ.publisher import RabbitPublisher
from app.rabbitMQ.consumer import RabbitConsumer
from app.core.config import settings
from app.core.logger_config import get_logger


logger = get_logger(__name__)

rabbit_publisher = RabbitPublisher(rabbit_url=settings.RABBIT_URL)

rabbit_consumer = RabbitConsumer(
    rabbit_url=settings.RABBIT_URL,
    queue_name="test_queue",
)


# Тестовая отправка в обменник
async def test_exchange():
    try:
        await rabbit_manager.init_rabbit(settings.RABBIT_URL)

        await rabbit_consumer.init_connection()

        test_message = await rabbit_publisher.publish_to_exchange(
            exchange_name="test_exchange",
            exchange_type="direct",
            routing_key="test.key",
            message_body={"test": "message", "data": "Hello World!"},
            content_type="application/json",
        )
        if test_message:
            logger.info(f"Сообщение успешно отправлено!")
            return True
        return False
    except Exception as e:
        logger.error(f"Произошла ошибка при отправке сообщения: {e}")
