# from fastapi import APIRouter, HTTPException, Depends
# from routes import pin
# from schemas.pin import PhotoSchema, BasePhoto, PhotoCreateSchema
# from sqlalchemy.ext.asyncio import AsyncSession
# from database import get_db

# router = APIRouter(tags=["Photos"])


# @router.get("/", response_model=list[PhotoSchema])
# async def get_photos(
#     session: AsyncSession = Depends(get_db),
# ):
#     return await pin.get_all_photos(session=session)


# @router.post("/", response_model=PhotoSchema)
# async def create_photo(
#     schema: PhotoCreateSchema,
#     session: AsyncSession = Depends(get_db),
# ):
#     return await pin.create_product(session=session, schema=schema)


# @router.get("/{photo.id}/", response_model=PhotoSchema)
# async def get_photos(
#     photo_id: int,
#     session: AsyncSession = Depends(get_db),
# ):
#     photo = await pin.get_photos_by_id(session=session, photo_id=photo_id)
#     if photo is not None:
#         return photo
#     raise HTTPException(status_code=404, detail="Photo {photo.id} not found!")
