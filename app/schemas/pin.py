from typing import Optional
from pydantic import BaseModel, Field


class PinBase(BaseModel):
    title: str = Field(..., max_length=100, description="Заголовок пина")
    description: str = Field(..., max_length=500, description="Описание пина")


class PinCreate(PinBase):
    user_id: int = Field(..., description="ID пользователя, создавшего пин")


class PinUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=100, description="Заголовок пина")
    description: Optional[str] = Field(
        None, max_length=500, description="Описание пина"
    )


class PinResponse(PinBase):
    id: int = Field(..., description="Уникальный идентификатор пина")
    user_id: int = Field(..., description="ID пользователя, создавшего пин")

    class Config:
        from_attributes = True
