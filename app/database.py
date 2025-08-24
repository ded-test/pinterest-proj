from contextlib import asynccontextmanager
from typing import AsyncGenerator
import redis
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from models.base import Base
from logger_config import get_logger

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
                database_url, decode_responses=True, encoding="utf-8"
            )
            self.redis.ping()
            self._database_url = database_url
            logger.info("Redis запущен")
        except Exception as e:
            self.redis = None
            raise RuntimeError(f"Ошибка запуска Redis: {e}")

    async def set(self, key: str, value: str, expire: Optional[int] = None):
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
