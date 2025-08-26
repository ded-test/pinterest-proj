from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class PhotoBase(BaseModel):
    title: Optional[str] = Field(None, description="Заголовок фотографии")
    url: str = Field(..., description="URL фотографии")
    width: int = Field(..., gt=0, description="Ширина изображения в пикселях")
    height: int = Field(..., gt=0, description="Высота изображения в пикселях")


class PhotoCreate(PhotoBase):
    pin_id: int = Field(..., description="ID пина, к которому привязана фотография")


class PhotoUpdate(BaseModel):
    title: Optional[str] = Field(None, description="Заголовок фотографии")
    url: Optional[str] = Field(None, description="URL фотографии")
    width: Optional[int] = Field(
        None, gt=0, description="Ширина изображения в пикселях"
    )
    height: Optional[int] = Field(
        None, gt=0, description="Высота изображения в пикселях"
    )


class PhotoResponse(PhotoBase):
    id: int = Field(..., description="Уникальный идентификатор фотографии")
    pin_id: int = Field(..., description="ID пина, к которому привязана фотография")
    created_at: datetime = Field(..., description="Дата и время создания")

    class Config:
        from_attributes = True


# class PhotoWithPin(PhotoResponse):
#     """Схема для фотографии с информацией о пине (если нужно)"""
#     # Здесь можно добавить вложенную схему пина, когда она будет готова
#     # pin: PinResponse
#     pass


# class PhotoList(BaseModel):
#     """Схема для списка фотографий с пагинацией"""
#     photos: list[PhotoResponse]
#     total: int = Field(..., description="Общее количество фотографий")
#     page: int = Field(1, description="Номер страницы")
#     per_page: int = Field(10, description="Количество элементов на странице")
