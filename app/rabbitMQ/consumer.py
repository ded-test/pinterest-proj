from app.core.logger_config import get_logger
import aio_pika


logger = get_logger(__name__)


class RabbitConsumer:
    def __init__(self, rabbit_url: str, queue_name: str) -> None:
        self.rabbit_url: str = rabbit_url
        self.queue_name: str = queue_name
        self.connection = None
        self.channel = None
        self.queue = None

    async def init_connection(
        self,
    ):
        try:

            self.connection = await aio_pika.connect_robust(self.rabbit_url)

            # Создание канала
            self.channel = await self.connection.channel()

            await self.channel.set_qos(
                prefetch_count=10
            )  # Запрашиваем до 10 сообщений от нашей очереди

            self.queue = await self.channel.declare_queue(
                self.queue_name, auto_delete=True
            )  # Объявляем очередь
            logger.info(f"Очередь: {self.queue_name} объявлена и готова к работе!")
            return self.queue
        except Exception as e:
            logger.error(f"Произошла ошибка при объявлении очереди: {e}")
            await self.close()
            raise

    # Что делаем с сообщениями из очереди
    async def message_processing(self):

        if self.queue is None:
            raise RuntimeError("Сначала вызови init_connection()")

        async with self.queue.iterator() as queue_iter:
            async for message in queue_iter:
                try:
                    async with message.process():
                        print(f"Получено сообщение: {message.body}")

                        if self.queue.name in message.body.decode():
                            break
                # Логируем ошибку, но продолжаем слушать очередь
                except Exception as e:
                    logger.error(f"Ошибка обработки сообщения {message.body} : {e}")
                    continue

    async def close(self):
        if self.connection:
            await self.connection.close()
            self.connection = None
            self.channel = None
            self.queue = None


rabbit_consumer = RabbitConsumer()
