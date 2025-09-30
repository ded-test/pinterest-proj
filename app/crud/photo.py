from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from security.password import verify_password
from models.user import User
from security.password import (
    get_password_hash,
    verify_password,
    validate_password_strength,
)
from schemas.user import UserCreate, UserUpdate, UserChangePassword, UserLogin
from core.logger_config import logger
from app.models.photo import Photo
from app.schemas.photo import PhotoCreate, PhotoUpdate


class PhotoCRUD:
    @staticmethod
    async def get_by_id(db: AsyncSession, photo_id: int) -> Optional[Photo]:
        try:
            result = await db.execute(select(Photo).filter(Photo.id == photo_id))
            photo = result.scalar_one_or_none()
            if not photo:
                logger.debug(f"Фото не найден по id: {photo_id}")
            return photo
        except Exception as e:
            logger.error(f"Ошибка при получении фото по id {photo_id}: {e}")
            raise

    @staticmethod
    async def get_all_photos(db: AsyncSession) -> list[Photo]:
        try:
            result = await db.execute(select(Photo))
            all_photos = result.scalars().all()
            if not all_photos:
                logger.debug(f"Фотографий не найдено")
            return all_photos
        except Exception as e:
            logger.error(f"Произошла ошибка получения всех фотографий: {e}")
            raise

    @staticmethod
    async def create_photo(db: AsyncSession, photo_data: PhotoCreate) -> Photo:
        try:
            photo_dict = photo_data.model_dump()
            photo = Photo(**photo_dict)
            db.add(photo)
            await db.commit()
            await db.refresh(photo)
            logger.info(f"Фото с ID: {photo.id} успешно создано")
            return photo
        except Exception as e:
            await db.rollback()
            logger.error(f"Произошла ошибка создании фото: {e}")
            raise

    @staticmethod
    async def update_photo(
        db: AsyncSession, photo_id: int, photo_update: PhotoUpdate
    ) -> Optional[Photo]:
        try:
            db_photo = await PhotoCRUD.get_by_id(db, photo_id)

            if not db_photo:
                logger.info(f"Обновление не удалось: фото с ID: {photo_id} не найдено")
                return db_photo

            update_data = photo_update.model_dump(exclude_unset=True)

            if not update_data:
                logger.info(f"Не удалось обновить фотографию с ID : {photo_id}")

            for field, value in update_data.items():
                setattr(db_photo, field, value)

            await db.commit()
            await db.refresh(db_photo)
            logger.info(f"Фото с ID {photo_id} успешно обновлено")
            return db_photo

        except Exception as e:
            logger.error(f"Произошла ошибка обновления фото: {e}")
            await db.rollback()
            raise

    @staticmethod
    async def delete_photo(db: AsyncSession, photo_id: int) -> bool:
        try:
            db_photo = await PhotoCRUD.get_by_id(db, photo_id)

            if not db_photo:
                logger.error(f"Фото с ID: {photo_id} не существует")
                return False

            await db.delete(db_photo)
            await db.commit()
            logger.info(f"Фото с ID: {photo_id} успешно удалено")
            return True

        except Exception as e:
            logger.error(f"Произошла ошибка удаления фото: {e}")
            await db.rollback()
            return False
