import bcrypt
import uuid

from app.core.logger_config import get_logger
from app.security.jwt import jwt_manager
from app.models.refresh_token import RefreshToken
from app.core.database import redis_manager
from datetime import datetime, timezone
from app.schemas.user import UserBase
from app.schemas.jwt_error import *
from sqlalchemy.ext.asyncio import AsyncSession

logger = get_logger(__name__)


class JWTCRUD:
    async def create_access_token(self, user: UserBase) -> str:
        try:
            payload = {
                "sub": str(user.id),
                "username": user.username,
            }
            token = jwt_manager.create_access_token(payload)
            return token
        except Exception:
            logger.exception("Ошибка создания access-токена")
            raise

    async def create_refresh_token(self, user: UserBase, db: AsyncSession) -> str:
        try:
            jti = str(uuid.uuid4())
            payload = {"sub": str(user.id), "token_type": "refresh", "jti": jti}
            token = jwt_manager.create_refresh_token(payload)

            token_data = jwt_manager.decode_refresh_token(token)
            exp_timestamp = token_data["exp"]

            token_hash = self._hash_token(token)

            await self._save_token_redis(user.id, jti, token_hash, exp_timestamp)
            await self._save_token_db(db, user.id, jti, token_hash, exp_timestamp)

            return token
        except Exception:
            logger.exception("Ошибка создания refresh-токена")
            raise

    def check_token(self, user_id: int, token: str) -> bool:
        try:
            token_data = jwt_manager.decode_refresh_token(token)
            jti = token_data["jti"]

            stored_hash = redis_manager.get(f"user:{user_id}:refresh_token:{jti}")

            if not stored_hash:
                return False

            return self._verify_token(stored_hash, token)

        except (JWTExpiredError, JWTInvalidTokenError):
            return False
        except Exception:
            logger.exception("Неожиданная ошибка при проверке токена")
            return False

    async def _save_token_redis(
        self, user_id: int, jti: str, token_hash: bytes, exp_timestamp: str
    ) -> None:
        key = f"user:{user_id}:refresh_token:{jti}"
        ttl = exp_timestamp - int(datetime.now(timezone.utc).timestamp())
        await redis_manager.set(key, token_hash, expire=ttl)

    async def _save_token_db(
        self,
        db: AsyncSession,
        user_id: int,
        jti: str,
        token_hash: bytes,
        exp_timestamp: int,
    ) -> None:

        expires_at = datetime.fromtimestamp(exp_timestamp, timezone.utc)
        db_token = RefreshToken(
            jti=jti,
            token_hash=token_hash,
            user_id=user_id,
            expires_at=expires_at,
        )
        db.add(db_token)
        await db.commit()
        await db.refresh(db_token)

    def _hash_token(self, token: str) -> bytes:
        return bcrypt.hashpw(token.encode(), bcrypt.gensalt())

    def _verify_token(self, stored_hash: bytes, token: str) -> bool:
        return bcrypt.checkpw(token.encode(), stored_hash)


jwt_crud = JWTCRUD()
