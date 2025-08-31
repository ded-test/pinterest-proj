from sqlalchemy.orm import mapped_column, Mapped
from sqlalchemy import DateTime
from base import Base
import datetime


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    id: Mapped[int] = mapped_column(primary_key=True)
    token_hash: Mapped[bytes] = mapped_column(unique=True, index=True)
    user_id: Mapped[int] = mapped_column(index=True)
    expires_at: Mapped[DateTime]
    is_revoked: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[DateTime] = mapped_column(default=datetime.utcnow)
