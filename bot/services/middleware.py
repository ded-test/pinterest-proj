from aiogram import BaseMiddleware
from aiogram.types import Update
from typing import Callable, Dict, Any, Awaitable
from services.database import AsyncSessionLocal
from models.user import User


class UserMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Update, Dict[str, Any]], Awaitable[Any]],
        event: Update,
        data: Dict[str, Any],
    ) -> Any:
        async with AsyncSessionLocal() as session:
            user = event.from_user
            if user:
                db_user = await session.get(User, user.id)
                if not db_user:
                    db_user = User(
                        user_id=user.id,
                        username=user.username,
                    )
                    session.add(db_user)
                    await session.commit()

                data["user"] = db_user

            return await handler(event, data)
