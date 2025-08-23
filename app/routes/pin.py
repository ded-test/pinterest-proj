"""
Create
Read
Update
Delete
"""

from sqlalchemy.ext.asyncio import AsyncSession
from models.photo import Photo
from sqlalchemy.engine import Result
from sqlalchemy import select
from schemas.pin import PhotoCreateSchema


async def get_all_photos(session: AsyncSession) -> list[Photo]:
    stmt = select(Photo).order_by(Photo.id)
    result: Result = await session.execute(stmt)
    photos = result.scalars().all()
    return list(photos)


async def get_photos_by_id(session: AsyncSession, photo_id) -> Photo | None:
    return await session.get(Photo, photo_id)


async def create_product(session: AsyncSession, schema: PhotoCreateSchema) -> Photo:
    photo = Photo(**schema.model_dump())
    session.add(photo)
    await session.commit()
    await session.refresh(photo)
    return photo
