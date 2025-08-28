from sqlalchemy import BigInteger, String
from sqlalchemy.orm import Mapped, mapped_column
from services.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(BigInteger, unique=True)
    username: Mapped[str] = mapped_column(String(100), nullable=True)
    is_admin: Mapped[bool] = mapped_column(default=False)

    def __repr__(self):
        return f"User({self.user_id}, {self.username})"
