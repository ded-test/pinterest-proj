from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.security.password import verify_password
from app.models.user import User
from app.security.password import (
    get_password_hash,
    verify_password,
    validate_password_strength,
)
from app.schemas.user import UserCreate, UserUpdate, UserChangePassword, UserLogin
from app.core.logger_config import logger
from app.models.pin import Pin
from app.schemas.pin import PinBase, PinUpdate, PinCreate
from app.models.photo import Photo


class PinCRUD:
    @staticmethod
    async def get_by_id(db: AsyncSession, pin_id: int) -> Optional[Pin]:
        try:
            result = await db.execute(select(Pin).filter(Pin.id == pin_id))
            pin = result.scalar_one_or_none()
            if not pin:
                logger.debug(f"Пин с ID: {pin_id} не найден")
            return pin
        except Exception as e:
            logger.error(f"Произошла ошибка получения пина: {e}")
            raise

    # Получает пользователя с пином и фото
    @staticmethod
    async def get_by_id_with_user(db: AsyncSession, pin_id: int) -> Optional[Pin]:
        try:
            result = await db.execute(
                select(Pin)
                .options(selectinload(Pin.photos), selectinload(Pin.user))
                .filter(Pin.id == pin_id)
            )
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Произошла ошибка получения пользователя с пином: {e}")
            raise

    @staticmethod
    async def get_all_pins(
        db: AsyncSession, skip: int = 0, limit: int = 100
    ) -> list[Pin]:
        try:
            result = await db.execute(
                select(Pin).options(selectinload(Pin.photos)).offset(skip).limit(limit)
            )  # Загружаем фото для всех пинов с пагинацией
            all_pins = result.scalars().all()
            if not all_pins:
                logger.debug("Ни одного пина не найдено")
            return all_pins

        except Exception as e:
            logger.error(f"Произошла ошибка получения всех пинов: {e}")
            raise

    @staticmethod
    async def create_pin(db: AsyncSession, pin_data: PinCreate, user_id : int) -> Pin:
        try:
            pin_dict = pin_data.model_dump()
            pin = Pin(**pin_dict, user_id=user_id)
            db.add(pin)
            await db.commit()
            await db.refresh(pin)
            logger.info(
                f"Пин с ID: {pin.id} успешно создан для пользователя: {user_id}"
            )
            return pin
        except Exception as e:
            logger.error(f"Произошла ошибка создания пина: {e}")
            await db.rollback()
            raise

    @staticmethod
    async def create_pin_with_photos(
        db: AsyncSession, user_id: int, pin_data: PinCreate, photos_data: List
    ) -> Pin:
        try:
            pin_dict = pin_data.model_dump()
            pin = Pin(**pin_dict, user_id=user_id)

            for photo_data in photos_data:
                pin_dict = pin_data.model_dump()
                photo = Photo(**photo_data, pin_id=pin.id)
                pin.photos.append(photo)

            db.add(pin)
            await db.commit()
            await db.refresh(pin)
            logger.info(f"Пин с ID: {pin.id} и {len(photos_data)} фото успешно создан")
            return pin
        except Exception as e:
            logger.error(f"Произошла ошибка создания пина с фото: {e}")
            await db.rollback()
            raise

    # Добавить фото к уже созданому пину
    @staticmethod
    async def add_photo_to_pin(
        db: AsyncSession, pin_id: int, photo_data
    ) -> Optional[Photo]:
        try:
            pin = await PinCRUD.get_by_id(db, pin_id)
            if not pin:
                logger.error(f"Пин с ID : {pin_id} не найден")
                return None

            photo_dict = photo_data.model_dump()
            photo = Photo(**photo_dict, pin_id=pin.id)
            db.add(photo)
            await db.commit()
            await db.refresh(photo)
            logger.info(f"Фото с ID: {photo.id} добавлено к пину {pin_id}")
            return photo
        except Exception as e:
            logger.error(f"Произошла ошибка добавление фото к пину: {e}")
            raise

    @staticmethod
    async def get_photos_by_pin(db: AsyncSession, pin_id: int) -> List[Photo]:

        try:
            result = await db.execute(select(Photo).filter(Photo.pin_id == pin_id))
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Ошибка при получении фото пина: {e}")
            raise

    @staticmethod
    async def update_pin(db: AsyncSession, pin_id: int, pin_data: PinUpdate) -> Pin:
        try:
            db_pin = await PinCRUD.get_by_id(pin_id)

            if not db_pin:
                logger.error(
                    f"Произошла ошибка обновления: пина с ID: {pin_id} не найден"
                )
                return None

            update_data = pin_data.model_dump(exclude_unset=True)

            if not update_data:
                logger.debug(f"Произошла ошибка обновления пина с ID: {pin_id}")
                return db_pin

            for field, value in update_data.items():
                setattr(db_pin, field, value)

            await db.commit()
            await db.refresh(db_pin)
            logger.info(f"Пин с ID: {pin_id} успешно обновлен")

            return db_pin

        except Exception as e:
            logger.error(f"Произошла ошибка обновления пина с ID : {pin_id}: {e}")
            await db.rollback()
            raise

    @staticmethod
    async def delete_pin(db: AsyncSession, pin_id: int) -> bool:
        try:
            db_pin = await PinCRUD.get_by_id(pin_id)

            if not db_pin:
                logger.error(
                    f"Произошла ошибка удаления: пина с ID: {pin_id} не найден"
                )
                return False

            await db.delete(db_pin)
            await db.commit()

            logger.info(f"Пин с ID: {pin_id} успешно удален ")
            return True

        except Exception as e:
            logger.error(f"Произошла ошибка удаления пина с ID: {pin_id} : {e}")
            await db.rollback()
            return False
