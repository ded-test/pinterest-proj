from contextlib import asynccontextmanager
from typing import AsyncGenerator
import redis.asyncio as redis
from typing import Optional, Union

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from app.models.base import Base
from app.core.logger_config import get_logger
from aio_pika import connect_robust
import asyncio
from app.core.config import settings

logger = get_logger(__name__)


class DBManager:
    def init_db(self, database_url: str):
        self.engine = create_async_engine(
            database_url,
            echo=True,
            pool_pre_ping=True,
        )
        self.session_factory = async_sessionmaker(
            bind=self.engine, expire_on_commit=False
        )
        self._database_url = database_url
        logger.info("База данных запущена")

    async def create_tables(self):
        if not self.engine:
            raise RuntimeError("Вызови init_db() сначала")
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Таблицы базы данных успешно созданы")

    async def drop_tables(self):
        if not self.engine:
            raise RuntimeError("Вызови init_db() сначала")

        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
        logger.info("Таблицы базы данных успешно удалены")

    async def recreate_tables(self):
        await self.drop_tables()
        await self.create_tables()

    async def close(self):
        if self.engine:
            await self.engine.dispose()
            self.engine = None
            self.session_factory = None
            self._database_url = None
            logger.info("DatabaseManager закрыт")

    @asynccontextmanager
    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        if not self.session_factory:
            raise RuntimeError("Вызови init_db() сначала")

        session = self.session_factory()
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


db_manager = DBManager()


class RedisManager:
    async def init_redis(self, database_url: str):
        try:
            self.redis = redis.from_url(
                database_url, decode_responses=False, encoding="utf-8"
            )
            await self.redis.ping()
            self._database_url = database_url
            logger.info("Redis запущен")
        except Exception as e:
            self.redis = None
            raise RuntimeError(f"Ошибка запуска Redis: {e}")

    async def set(
        self, key: str, value: Union[str, bytes], expire: Optional[int] = None
    ):
        if not self.redis:
            raise RuntimeError("Вызови init_db() сначала")
        await self.redis.set(key, value, ex=expire)

    async def get(self, key: str) -> Optional[str]:
        if not self.redis:
            raise RuntimeError("Вызови init_db() сначала")
        return await self.redis.get(key)

    async def delete(self, key: str):
        if not self.redis:
            raise RuntimeError("Вызови init_db() сначала")
        await self.redis.delete(key)

    async def close(self):
        if self.redis:
            await self.redis.close()
            self.redis = None
            self._database_url = None
            logger.info("RedisManager закрыт")

    @asynccontextmanager
    async def get_client(self) -> AsyncGenerator[redis.Redis, None]:
        if not self.redis:
            raise RuntimeError("Вызови init_db() сначала")

        try:
            yield self.redis
        finally:
            pass


redis_manager = RedisManager()


class RabbitManager:
    def __init__(self):
        self._connection = None
        self._rabbit_url = None
        self._channel = None
        self._is_initialized = False

    async def init_rabbit(self, rabbit_url: str):
        try:
            self._rabbit_url = rabbit_url
            self._connection = await connect_robust(rabbit_url)
            self._channel = await self._connection.channel()
            self._is_initialized = True

            logger.info("RabbitMQ параметры установлены")
        except Exception as e:
            self._connection = None
            self._channel = None
            self._is_initialized = False
            logger.error(f"Ошибка подключения RabbitMQ: {e}")
            raise RuntimeError(f"Ошибка запуска RabbitMQ: {e}") from e

    async def check_connection(self) -> bool:
        if not self._is_initialized:
            raise RuntimeError("Ошибка подключения! Сначала вызови init_rabbit()")
        try:
            if self._connection and not self._connection.is_closed:
                logger.debug("Соединение с RabbitMQ в порядке!")
                return True
            return False
        except Exception as e:
            logger.error(f"Произошла непредвиденная ошибка {e}")
            return False

    async def close(self):
        if self._connection:
            await self._connection.close()
            self._connection = None
            self._is_initialized = False
            self._channel = None
            self._rabbit_url = None
            logger.info("RabbitManager закрыт")


rabbit_manager = RabbitManager()

