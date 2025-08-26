from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    id: int
    username: str
    password: bytes
    email: EmailStr | None = None
    
class UserCreate(UserBase):
    