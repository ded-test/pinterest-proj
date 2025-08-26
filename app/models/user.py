from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base
from app.models.pin import Pin
from sqlalchemy import String


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(50), nullable=False)
    email: Mapped[str] = mapped_column(unique=True)
    hashed_password: Mapped[bytes]
    pins: Mapped[list["Pin"]] = relationship("Pin", back_populates="user")
