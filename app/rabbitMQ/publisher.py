from app.core.database import rabbit_manager
from app.core.logger_config import get_logger
import aio_pika
from typing import Optional
import json


logger = get_logger(__name__)


class RabbitPublisher:
    def __init__(self, rabbit_url: str) -> None:
        self.rabbit_url = rabbit_url

    # Создаем обменник в который будем складывать сообщения , что бы потом забирать из него

    async def publish_to_exchange(
        self,
        exchange_name: str,
        exchange_type: str = "direct",
        routing_key: str = "",
        message_body: str = "",
        content_type: str = "application/json",
        headers: Optional[dict] = None,
        durable: bool = True,
    ) -> bool:

        # exchange_type: Тип обменника (direct, fanout, topic, headers)

        # routing_key: Ключ маршрутизации

        # Проверяем соединение , создаем канал для подключения , и объявляем обменник

        # durable: Сохранять ли exchange после перезагрузки
        try:
            if not rabbit_manager._is_initialized:
                await rabbit_manager.init_rabbit(self.rabbit_url)

            channel = rabbit_manager._channel

            exchange_type_enum = aio_pika.ExchangeType(exchange_type.lower())

            exchange = await channel.declare_exchange(
                exchange_name,
                type=exchange_type_enum,
                durable=durable,
            )

            # Серилизация данных в сообщении если контент тайп json то раскодируем его и переводим в байты
            if content_type == "application/json":
                message_body = json.dumps(message_body).encode()
            else:
                message_body = str(message_body).encode()

            message = aio_pika.Message(
                body=message_body,
                content_type=content_type,
                headers=headers or {},
            )

            await exchange.publish(message, routing_key=routing_key)
            logger.info(
                f"Сообщение отправленно в обменник : {exchange_name} с routing key: {routing_key}"
            )
            return True
        except Exception as e:
            logger.error(f"Произошла непредвиденная ошибка публикации: {e}")
            return False
