from pydantic import BaseModel, EmailStr, ConfigDict, field_validator, model_validator
from typing import Optional
from app.security.password import (
    validate_password_strength,
    get_password_hash,
    verify_password,
)


class UserBase(BaseModel):
    username: str
    email: EmailStr
    pins: list

    @field_validator("username")
    @classmethod
    def validate_names(cls, v):
        if not v or len(v.strip()) < 2:
            raise ValueError("Username должно содержать не менее 2 символов")
        return v.strip().title()


class UserCreate(UserBase):
    password: str
    confirm_password: str

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, v):
        return validate_password_strength(v)

    @model_validator(mode="after")
    def passwords_match(self):
        if self.password != self.confirm_password:
            raise ValueError("Пароли не совпадают")
        return self

    def get_password_hash(self) -> tuple[str, str]:
        return get_password_hash(self.password)


class UserUpdate(UserBase):
    username: Optional[str]
    email: Optional[EmailStr]
    password: Optional[str]

    @field_validator("username")
    @classmethod
    def validate_names(cls, v):
        if not v or len(v.strip()) < 2:
            raise ValueError("Username должно содержать не менее 2 символов")
        return v.strip().title()


class UserChangePassword(BaseModel):
    current_password: str
    new_password: str
    confirm_new_password: str

    @field_validator("new_password")
    @classmethod
    def validate_password_strength(cls, v):
        return validate_password_strength(v)

    @model_validator(mode="after")
    def passwords_match(self):
        if self.new_password != self.confirm_new_password:
            raise ValueError("Passwords don't match")
        return self

    def get_password_hash(self) -> tuple[str, str]:
        return get_password_hash(self.new_password)


class UserResponse(UserBase):

    model_config = ConfigDict(from_attributes=True)

    id: int
