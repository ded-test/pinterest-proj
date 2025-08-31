from typing import AsyncGenerator

import redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import db_manager, redis_manager


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    async with db_manager.get_session() as session:
        yield session


async def get_redis() -> AsyncGenerator[redis.Redis, None]:
    async with redis_manager.get_client() as redis_client:
        yield redis_client
