from app.core.logger_config import get_logger
import aio_pika
from typing import Optional, Callable, Awaitable
from app.core.database import rabbit_manager

logger = get_logger(__name__)


class RabbitConsumer:
    def __init__(self, rabbit_url: str, queue_name: str) -> None:
        self.rabbit_url: str = rabbit_url
        self.queue_name: str = queue_name
        self.connection = None
        self.channel = None
        self.queue = None
        self.exchange = None

    async def init_connection(
        self,
        routing_key: str = "",
        exchange_name: Optional[str] = None,
        exchange_type: str = "direct",
    ):
        try:

            self.connection = await aio_pika.connect_robust(self.rabbit_url)

            # Создание канала
            logger.info("Создание канала...")
            self.channel = await self.connection.channel()

            await self.channel.set_qos(
                prefetch_count=10
            )  # Запрашиваем до 10 сообщений из нашей очереди
            logger.info(f"Объявление очереди: {self.queue_name}")

            self.queue = await self.channel.declare_queue(
                self.queue_name, auto_delete=False, durable=True
            )

            # Объявляем очередь

            logger.info("Очередь создана")
            if exchange_name and routing_key:
                logger.info(f"🔄 Объявление exchange: {exchange_name}")
                exchange = await self.channel.declare_exchange(
                    exchange_name,
                    type=aio_pika.ExchangeType(exchange_type).lower(),
                    durable=True,
                )
                logger.info("Exchange создан")
                print(f"🔗 Привязка очереди к exchange с ключом: {routing_key}")
                await self.queue.bind(exchange, routing_key)
                logger.info("Привязка выполнена")
                logger.info(
                    f"Очередь: {self.queue_name} объявлена и привязана к {exchange_name} , с ключом {routing_key} работе!"
                )
            return self.queue
        except Exception as e:
            logger.error(f"Произошла ошибка при объявлении очереди: {e}")
            await self.close()
            raise

    # Что делаем с сообщениями из очереди
    async def message_processing(
        self, callback: Optional[Callable[[str], Awaitable[bool]]] = None
    ):

        if self.queue is None:
            raise RuntimeError("Сначала вызови init_connection()")

        async with self.queue.iterator() as queue_iter:
            async for message in queue_iter:
                try:

                    logger.info(f"Получено сообщение: {message.body}")

                    body = message.body.decode()
                    logger.info(f"Получено сообщение: {body}")

                    # Логика подтверждения сообщения (Кастомный сервис должен отправить в консюмера callback с подтверждением получения)

                    success = True
                    if callback:
                        success = await callback(body)

                    if success:
                        await message.ack()
                        logger.debug(f"Сообщение успешно подтверждено в Rabbit MQ!")
                    else:
                        await message.nack(requeue=False)
                        logger.warning(f"Сообщение было отклонено(не доставлено)")

                # Логируем ошибку, но продолжаем слушать очередь
                except Exception as e:
                    try:
                        await message.nack(requeue=False)
                    except:
                        pass
                    logger.error(f"Ошибка обработки сообщения: {e}")
                    continue

    async def close(self):
        if self.connection:
            await self.connection.close()
            self.connection = None
            self.channel = None
            self.queue = None
            self.exchange = None
