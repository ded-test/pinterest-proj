from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from typing import Optional
from app.models.base import Base
from sqlalchemy import ForeignKey
# from app.models.__init__ import Pin


class Photo(Base):
    __tablename__ = "photos"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[Optional[str]] = mapped_column(nullable=True)
    url: Mapped[str] = mapped_column(nullable=True, unique=True)
    width: Mapped[int] = mapped_column(nullable=False)
    height: Mapped[int] = mapped_column(nullable=False)
    pin_id: Mapped[int] = mapped_column(ForeignKey("pins.id", ondelete="CASCADE"))
    created_at: Mapped[datetime] = mapped_column(default=datetime.now)
    pin: Mapped["Pin"] = relationship("Pin", back_populates="photos")
