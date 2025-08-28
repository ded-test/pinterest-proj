from sqlalchemy.orm import Mapped, mapped_column, relationship
from models.base import Base
from sqlalchemy import ForeignKey, String


class Pin(Base):
    __tablename__ = "pins"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(100))
    description: Mapped[str] = mapped_column(String(500))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    photos: Mapped[list["Photo"]] = relationship(
        "Photo", back_populates="pin", cascade="all, delete-orphan"
    )
    user: Mapped["User"] = relationship("User", back_populates="pins")
