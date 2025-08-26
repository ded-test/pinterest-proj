from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional
from app.security.authentication import secure_password


class UserBase(BaseModel):
    username: str
    email: EmailStr
    pins: list


class UserCreate(UserBase):
    password: str
    confirm_password: str


class UserUpdate(UserBase):
    username: Optional[str]
    email: Optional[EmailStr]
    password: Optional[str]


class UserChangePassword(BaseModel):
    current_password: str
    new_password: str
    confirm_new_password: str


class UserResponse(UserBase):

    model_config = ConfigDict(from_attributes=True)

    id: int
