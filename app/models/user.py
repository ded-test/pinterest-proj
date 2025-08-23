from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime, timezone
from typing import Optional
from models.base import Base
from pin import Pin
from sqlalchemy import String


class User(Base):
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(50), nullable=False)
    email: Mapped[str] = mapped_column(unique=True)
    hashed_password: Mapped[str]
    is_active: Mapped[bool] = mapped_column(default=True)
    avatar_url: Mapped[Optional[str]]
    created_at: Mapped[datetime] = mapped_column(default=datetime.now(timezone.utc))
    pins: Mapped[list["Pin"]] = relationship("Pin", back_populates="user")
