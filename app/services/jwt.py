import bcrypt
import jwt
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPrivateKey
from datetime import datetime, timedelta, timezone
from logger_config import get_logger


logger = get_logger(__name__)


class JWTPrivateKeyGenerationError(Exception):
    pass


class JWTPrivateKeySaveError(Exception):
    pass


def generate_private_key(
    public_exponent: int = 65537, key_size: int = 2048
) -> RSAPrivateKey:
    try:
        return rsa.generate_private_key(
            public_exponent=public_exponent,
            key_size=key_size,
        )
    except Exception as e:
        logger.error(f"Ошибка создания JWTPrivateKey: {e}", exc_info=True)
        raise JWTPrivateKeyGenerationError(
            f"Ошибка создания приватного ключа: {e}"
        ) from e


def save_private_key(
    private_key,
    filename="jwt_private.pem",
    encoding=serialization.Encoding.PEM,
    format=serialization.PrivateFormat.PKCS8,
    encryption_algorithm=serialization.NoEncryption(),
):

    try:
        with open(filename, "wb") as f:
            f.write(
                private_key.private_bytes(
                    encoding=encoding,
                    format=format,
                    encryption_algorithm=encryption_algorithm,
                )
            )
    except Exception as e:
        logger.error(f"Ошибка сохранения JWTPrivateKey: {e}", exc_info=True)
        raise JWTPrivateKeySaveError(f"Ошибка сохранения приватного ключа: {e}") from e


class JWTPublicKeySaveError(Exception):
    pass


def save_public_key(
    public_key,
    filename="jwt_public.pem",
    encoding=serialization.Encoding.PEM,
    format=serialization.PublicFormat.SubjectPublicKeyInfo,
):

    try:
        with open(filename, "wb") as f:
            f.write(
                public_key.public_bytes(
                    encoding=encoding,
                    format=format,
                )
            )
    except Exception as e:
        logger.error(f"Ошибка сохранения JWTPublicKey: {e}", exc_info=True)
        raise JWTPublicKeySaveError(f"Ошибка сохранения публичного ключа: {e}") from e


class JWTEncodeError(Exception):
    pass


class JWTEncoder:
    def __init__(self, private_key: rsa.RSAPrivateKey):
        self.private_key = private_key

    def encode_jwt(
        self,
        payload: dict,
        algorithm: str = "RS256",
        expire_min: int = 30,
    ) -> str:

        try:
            to_encode = payload.copy()
            expire = datetime.now(timezone.utc) + timedelta(minutes=expire_min)
            to_encode.update(
                {
                    "exp": int(expire.timestamp()),
                    "iat": int(datetime.now(timezone.utc).timestamp()),
                }
            )

            encoded = jwt.encode(to_encode, self.private_key, algorithm=algorithm)

            return encoded

        except Exception as e:
            logger.error(f"Ошибка кодирования JWT: {e}", exc_info=True)
            raise JWTEncodeError(f"Ошибка кодирования: {e}") from e


class JWTDecodeError(Exception):
    pass


class JWTDecoder:
    def __init__(self, public_key: rsa.RSAPublicKey):
        self.public_key = public_key

    def decode_jwt(self, token: str, algorithms: list[str] = None):
        if algorithms is None:
            algorithms = ["RS256"]
        try:
            decoded = jwt.decode(
                token,
                self.public_key,
                algorithms=algorithms,
                options={"require": ["exp"]},
            )
            return decoded

        except Exception as e:
            logger.error(f"Ошибка декодирования:{e}", exc_info=True)
            raise JWTDecodeError(f"Не удалось обработать данные") from e


def hash_password(password: str) -> bytes:
    salt = bcrypt.gensalt()
    pwd_bytes: bytes = password.encode()
    return bcrypt.hashpw(pwd_bytes, salt)


def validate_password(
    password: str,
    hash_password: bytes,
) -> bool:
    return bcrypt.checkpw(
        password=password.encode(),
        hashed_password=hash_password,
    )
