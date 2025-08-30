import bcrypt
import jwt
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPrivateKey
from datetime import datetime, timedelta, timezone


from app.core.logger_config import get_logger
from jwt import ExpiredSignatureError, InvalidTokenError, InvalidSignatureError
from app.core.config import JWTConfig


logger = get_logger(__name__)  # Инициализация логов


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
        logger.error(f"Ошибка создания приватного ключа", exc_info=True)
        raise JWTPrivateKeyGenerationError(f"Ошибка обработки данных") from e


def save_private_key(
    private_key,
    filename=None,
    encoding=serialization.Encoding.PEM,
    format=serialization.PrivateFormat.PKCS8,
    encryption_algorithm=serialization.NoEncryption(),
):
    config = JWTConfig.get_jwt_config()
    if filename is None:
        filename = config.priv_filename

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
        logger.error(f"Ошибка сохранения приватного ключа", exc_info=True)
        raise JWTPrivateKeySaveError(f"Ошибка сохранения приватного ключа") from e


class JWTPublicKeySaveError(Exception):
    pass


def save_public_key(
    public_key,
    filename=None,
    encoding=serialization.Encoding.PEM,
    format=serialization.PublicFormat.SubjectPublicKeyInfo,
):
    config = JWTConfig.get_jwt_config()
    if filename is None:
        filename = config.pub_filename

    try:
        with open(filename, "wb") as f:
            f.write(
                public_key.public_bytes(
                    encoding=encoding,
                    format=format,
                )
            )
    except Exception as e:
        logger.error(f"Ошибка сохранения публичного ключа", exc_info=True)
        raise JWTPublicKeySaveError(f"Ошибка сохранения публичного ключа") from e


class JWTEncodeError(Exception):  # Общая ошибка кодирования JWT
    pass


class JWTInvalidPayloadError(JWTEncodeError):  # Не верный payload
    pass


class JWTAlgorithmError(JWTEncodeError):  # Не поддерживаемый алгоритм
    pass


class JWTKeyError(JWTEncodeError):  # Ошибка ключа
    pass


class JWTExpirationError(JWTEncodeError):  # Ошибка exp(времени жизни токена)
    pass


class JWTEncoder:
    def __init__(self, private_key: rsa.RSAPrivateKey):
        self.private_key = private_key
        self.config = JWTConfig.get_jwt_config()

    def encode_jwt(
        self,
        payload: dict,
        algorithm: str = None,
        expire_min: int = None,
    ) -> str:

        try:
            # Валидация и инициализация
            if not isinstance(payload, dict):
                raise JWTInvalidPayloadError("Payload должен быть словарем")

            if algorithm is None:
                algorithm = self.config.algorithm

            if expire_min is None:
                expire_min = self.config.token_expire_minutes

            if expire_min <= 0:
                raise JWTExpirationError(f"Время жизни токена должно быть больше нуля")

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

        except ValueError as e:
            if "Could not serialize" in str(e):
                raise JWTInvalidPayloadError(
                    "Невозможно сеарилизовать данные в payload"
                ) from e
            logger.error(f"ValueError при кодировании ", exc_info=True)
            raise JWTEncodeError(f"Ошибка кодирования ") from e

        except TypeError as e:
            logger.error(f"TypeError при кодировании", exc_info=True)
            raise JWTEncodeError(f"Ошибка при кодировании ") from e
        except Exception as e:
            logger.error(f"Ошибка кодирования JWT: ", exc_info=True)
            raise JWTEncodeError(f"Неожиданая ошибка кодирования") from e


class JWTDecodeError(Exception):
    pass


class JWTExpiredError(JWTDecodeError):
    pass


class JWTInvalidSignatureError(JWTDecodeError):
    pass


class JWTInvalidTokenError(JWTDecodeError):
    pass


class JWTFormatError(JWTDecodeError):
    pass


class JWTDecoder:
    def __init__(self, public_key: rsa.RSAPublicKey):
        self.public_key = public_key
        self.config = JWTConfig.get_jwt_config()

    def decode_jwt(self, token: str, algorithms: list[str] = None, **kwargs):

        try:
            if algorithms is None:
                algorithms = self.config.default_algorithms

            decoded = jwt.decode(
                token,
                self.public_key,
                algorithms=algorithms,
                # обязательно проверять наличие и валидность поля exp
                options={
                    "require": ["exp"],
                    "verify_signature": True,
                    **kwargs.get("options", {}),
                },  # получаем дополнительные options из параметров
                **{
                    k: v for k, v in kwargs.items() if k != "options"
                },  # Ищем в kwargs ключ "options" , если его нет - возвращаем пустой словарь {}
                # Распаковка словаря и объединение настроек с пользовательскими
            )
            return decoded

        except ExpiredSignatureError as e:
            logger.warning(f"Срок действия токена не действителен", exc_info=True)
            raise JWTExpiredError("Токен просрочен") from e

        except InvalidSignatureError as e:
            logger.warning(f"Неверная подпись токена")
            raise JWTInvalidSignatureError("Неверная подпись токена") from e

        except InvalidTokenError as e:
            logger.warning(f"Не валидный токен ", exc_info=True)
            raise JWTInvalidTokenError(f"Не валидный токен") from e

        except Exception as e:
            logger.error(f"Неожиданная ошибка декодирования", exc_info=True)
            raise JWTDecodeError(f"Ошибка декодирования") from e
