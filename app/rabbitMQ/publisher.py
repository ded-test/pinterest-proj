import asyncio

import asyncio
from app.core.config import Settings
from app.core.database import rabbit_manager
from app.core.logger_config import get_logger

logger = get_logger(__name__)


async def main():
    # Инициализация и проверка соединения
    try:
        settings = Settings()

        await rabbit_manager.init_rabbit(settings.RABBIT_URL)
        is_connected = rabbit_manager.check_connection()
        connection = rabbit_manager.connection()
        logger.info("Соединение с RabbitMQ создано", connection)
        while True:
            pass

    except Exception as e:
        logger.error(f"Произошла непредвиденная ошибка: {e}")


if __name__ == "__main__":
    asyncio.run(main())
