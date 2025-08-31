from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base
from app.models.pin import Pin
from sqlalchemy import String, DateTime
import datetime


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    hashed_password: Mapped[bytes] = mapped_column(nullable=False)

    pins: Mapped[list["Pin"]] = relationship(
        "Pin", back_populates="user", cascade="all, delete-orphan", lazy="selectin"
    )
