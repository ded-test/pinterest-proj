from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.security.password import verify_password
from app.models.user import User
from app.security.password import (
    get_password_hash,
    verify_password,
    validate_password_strength,
)
from app.schemas.user import UserCreate, UserUpdate, UserChangePassword, UserLogin
from app.core.logger_config import logger


class UserCRUD:

    @staticmethod
    async def get_by_id(db: AsyncSession, user_id: int) -> Optional[User]:
        try:
            result = await db.execute(select(User).filter(User.id == user_id))
            user = result.scalar_one_or_none()
            if not user:
                logger.debug(f"Пользователь не найден по id: {user_id}")
            return user
        except Exception as e:
            logger.error(f"Ошибка при получении пользователя по id {user_id}: {e}")
            raise

    @staticmethod
    async def get_by_email(db: AsyncSession, email: str) -> Optional[User]:
        try:
            result = await db.execute(select(User).filter(User.email == email))
            user = result.scalar_one_or_none()
            if not user:
                logger.debug(f"Пользователь не найден по email: {email}")
            return user
        except Exception as e:
            logger.error(f"Ошибка при получении пользователя по email {email}: {e}")
            raise

    @staticmethod
    async def get_by_username(db: AsyncSession, username: str) -> Optional[User]:
        try:
            result = await db.execute(select(User).filter(User.username == username))
            user = result.scalar_one_or_none()
            if not user:
                logger.debug(
                    f"Пользователь не найден по имени пользователя: {username}"
                )
            return user
        except Exception as e:
            logger.error(
                f"Ошибка при получении пользователя по имени пользователя {username}: {e}"
            )
            raise

    @staticmethod
    async def create(db: AsyncSession, user_create: UserCreate) -> User:
        try:
            existing_email = await UserCRUD.get_by_email(db, user_create.email)
            if existing_email:
                logger.warning(
                    f"Создание пользователя не удалось: email {user_create.email} уже существует"
                )
                raise ValueError("Пользователь с такой почтой уже существует")

            existing_username = await UserCRUD.get_by_username(db, user_create.username)
            if existing_username:
                logger.warning(
                    f"Создание пользователя не удалось: имя пользователя {user_create.username} уже существует"
                )
                raise ValueError("Пользователь с таким именем уже существует")

            hashed_password = get_password_hash(user_create.password)

            db_user = User(
                username=user_create.username,
                email=user_create.email,
                hashed_password=hashed_password,
            )

            db.add(db_user)
            await db.commit()
            await db.refresh(db_user)

            logger.info(
                f"Пользователь успешно создан: id={db_user.id}, email={db_user.email}"
            )
            return db_user

        except ValueError as e:
            logger.warning(f"Ошибка валидации при создании пользователя: {e}")
            await db.rollback()
            raise
        except Exception as e:
            logger.error(f"Ошибка при создании пользователя: {e}")
            await db.rollback()
            raise

    @staticmethod
    async def authenticate(db: AsyncSession, user_login: UserLogin) -> Optional[User]:
        try:
            db_user = await UserCRUD.get_by_username(db, user_login.username)
            if not db_user:
                logger.warning(
                    f"Неудачный вход: пользователь {user_login.username} не найден"
                )
                return None

            if not verify_password(user_login.password, db_user.hashed_password):
                logger.warning(
                    f"Неудачный вход: неверный пароль для пользователя {user_login.username}"
                )
                return None

            logger.info(f"Успешный вход: пользователь {user_login.username}")
            return db_user

        except Exception as e:
            logger.error(
                f"Ошибка при аутентификации пользователя {user_login.username}: {e}"
            )
            return None

    @staticmethod
    async def update(
        db: AsyncSession, user_id: int, user_update: UserUpdate
    ) -> Optional[User]:
        try:
            db_user = await UserCRUD.get_by_id(db, user_id)
            if not db_user:
                logger.warning(
                    f"Обновление не удалось: пользователь {user_id} не найден"
                )
                return None

            if user_update.email and user_update.email != db_user.email:
                existing_email = await UserCRUD.get_by_email(db, user_update.email)
                if existing_email:
                    logger.warning(
                        f"Обновление не удалось: email {user_update.email} уже существует"
                    )
                    raise ValueError("Пользователь с такой почтой уже существует")

            if user_update.username and user_update.username != db_user.username:
                existing_username = await UserCRUD.get_by_username(
                    db, user_update.username
                )
                if existing_username:
                    logger.warning(
                        f"Обновление не удалось: имя пользователя {user_update.username} уже существует"
                    )
                    raise ValueError("Пользователь с таким именем уже существует")

            update_data = user_update.model_dump(exclude_unset=True)

            for field, value in update_data.items():
                setattr(db_user, field, value)

            await db.commit()
            await db.refresh(db_user)

            logger.info(f"Пользователь успешно обновлён: id={user_id}")
            return db_user

        except ValueError as e:
            logger.warning(f"Ошибка валидации при обновлении пользователя: {e}")
            await db.rollback()
            raise
        except Exception as e:
            logger.error(f"Ошибка при обновлении пользователя {user_id}: {e}")
            await db.rollback()
            raise

    @staticmethod
    async def change_password(
        db: AsyncSession, user_id: int, password_change: UserChangePassword
    ) -> Optional[User]:
        try:
            db_user = await UserCRUD.get_by_id(db, user_id)
            if not db_user:
                logger.warning(
                    f"Смена пароля не удалась: пользователь {user_id} не найден"
                )
                return None

            if not await verify_password(
                password_change.current_password, db_user.hashed_password
            ):
                logger.warning(
                    f"Смена пароля не удалась: неверный текущий пароль для пользователя {user_id}"
                )
                raise ValueError("Неверный текущий пароль")

            validate_password_strength(password_change.new_password)
            hashed_password = get_password_hash(password_change.new_password)

            db_user.hashed_password = hashed_password
            await db.commit()
            await db.refresh(db_user)

            password_change.current_password = None
            password_change.new_password = None

            logger.info(f"Пароль успешно изменён для пользователя: {user_id}")
            return db_user

        except ValueError as e:
            logger.warning(
                f"Ошибка валидации при смене пароля для пользователя {user_id}: {e}"
            )
            await db.rollback()
            raise
        except Exception as e:
            logger.error(f"Ошибка при смене пароля для пользователя {user_id}: {e}")
            await db.rollback()
            raise

    @staticmethod
    async def delete(db: AsyncSession, user_id: int) -> bool:
        try:
            db_user = await UserCRUD.get_by_id(db, user_id)
            if not db_user:
                logger.warning(f"Удаление не удалось: пользователь {user_id} не найден")
                return False

            await db.delete(db_user)
            await db.commit()

            logger.info(f"Пользователь успешно удалён: {user_id}")
            return True

        except Exception as e:
            logger.error(f"Ошибка при удалении пользователя {user_id}: {e}")
            await db.rollback()
            raise
