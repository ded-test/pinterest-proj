from datetime import datetime, timezone, timedelta
from typing import Optional, Sequence
import jwt
from jwt.exceptions import (
    ExpiredSignatureError,
    InvalidSignatureError,
    InvalidTokenError,
)
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from app.schemas.jwt_error import *
from app.core.logger_config import get_logger
from app.core.config import settings
import os
import uuid

logger = get_logger(__name__)


def load_private_key(path: str):
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    full_path = os.path.join(base_dir, path)
    with open(full_path, "rb") as f:
        return serialization.load_pem_private_key(f.read(), password=None)


def load_public_key(path: str):
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    full_path = os.path.join(base_dir, path)
    with open(full_path, "rb") as f:
        return serialization.load_pem_public_key(f.read())


class JWTManager:
    def __init__(self):
        # Access токены
        self.access_private_key = load_private_key(settings.ACCESS_PRIVATE_KEY_PATH)
        self.access_public_key = load_public_key(settings.ACCESS_PUBLIC_KEY_PATH)
        self.access_expire = settings.ACCESS_TOKEN_EXPIRE_MIN

        # Refresh токены
        self.refresh_private_key = load_private_key(settings.REFRESH_PRIVATE_KEY_PATH)
        self.refresh_public_key = load_public_key(settings.REFRESH_PUBLIC_KEY_PATH)
        self.refresh_expire = settings.REFRESH_TOKEN_EXPIRE_MIN

        # Алгоритм
        self.algorithm = settings.JWT_ALGORITHM

    def _encode(
        self, payload: dict, private_key: rsa.RSAPrivateKey, expire_min: int
    ) -> str:
        # сразу проверка на словарь
        if not isinstance(payload, dict):
            raise JWTInvalidPayloadError("Payload должен быть словарем")

        now = datetime.now(timezone.utc)
        to_encode = payload.copy()

        to_encode.update(
            {
                "iat": int(now.timestamp()),  # когда токен создан
                "exp": int(
                    (now + timedelta(minutes=expire_min)).timestamp()
                ),  # когда токен истечёт
            }
        )

        try:
            # jwt.encode берёт payload, подписывает приватным ключом и возвращает строку JWT
            return jwt.encode(to_encode, private_key, algorithm=self.algorithm)

        except (ValueError, TypeError) as e:  # проблемы с сериализацией payload
            if "Could not serialize" in str(e):
                raise JWTInvalidPayloadError(
                    "Невозможно сериализовать данные в payload"
                ) from e
            logger.error("Ошибка кодирования JWT", exc_info=True)
            raise JWTEncodeError("Ошибка кодирования JWT") from e

        except Exception as e:  # остальные ошибки
            logger.error("Неожиданная ошибка кодирования JWT", exc_info=True)
            raise JWTEncodeError("Неожиданная ошибка кодирования JWT") from e

    def _decode(
        self,
        token: str,
        public_key: rsa.RSAPublicKey,  # публичный ключ для проверки подписи
        algorithms: Optional[
            Sequence[str]
        ] = None,  # список алгоритмов, которые разрешены для декодирования
        **kwargs,  # Любые дополнительные параметры для jwt.decode
    ) -> dict:

        algorithms = algorithms or [self.algorithm]
        options = {
            "require": ["exp"],
            "verify_signature": True,
        }  # проверка поля время и подпись токена публичным ключом
        options.update(
            kwargs.pop("options", {})
        )  # если пользователь передал свои опции, объединяем с дефолтными

        try:
            return jwt.decode(
                token, public_key, algorithms=algorithms, options=options, **kwargs
            )

        # токен просрочен.
        except ExpiredSignatureError as e:
            logger.warning("JWT токен просрочен", exc_info=True)
            raise JWTExpiredError("Токен просрочен") from e

        # подпись не совпадает с публичным ключом
        except InvalidSignatureError as e:
            logger.warning("JWT токен с неверной подписью")
            raise JWTInvalidSignatureError("Неверная подпись токена") from e

        # токен некорректный
        except InvalidTokenError as e:
            logger.warning("JWT токен невалидный", exc_info=True)
            raise JWTInvalidTokenError("Не валидный токен") from e

    # Access токены
    def create_access_token(self, payload: dict) -> str:
        payload_with_jti = payload.copy()
        payload_with_jti["jti"] = str(uuid.uuid4())
        return self._encode(payload, self.access_private_key, self.access_expire)

    def decode_access_token(self, token: str) -> dict:
        return self._decode(token, self.access_public_key)

    # Refresh токены
    def create_refresh_token(self, payload: dict) -> str:
        return self._encode(payload, self.refresh_private_key, self.refresh_expire)

    def decode_refresh_token(self, token: str) -> dict:
        return self._decode(token, self.refresh_public_key)


jwt_manager = JWTManager()
