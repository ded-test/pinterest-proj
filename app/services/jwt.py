import bcrypt
import jwt
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from datetime import datetime, timedelta, timezone
import logging
import asyncio



"""
Сделай
 - разделение ответственности в виде классов
 - в асинхронность переведи
 - обработку ошибок в encode_jwt и decode_jwt 
"""
logger = logging.getLogger(__name__)

private_key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=2048,
)

with open("jwt_private.pem", "wb") as f:
    f.write(
        private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        )
    )

public_key = private_key.public_key()


with open("jwt_public.pem", "wb") as f:
    f.write(
        public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )
    )

class JWTEncodeError(Exception):
    pass


class JWTEncoder:
    def __init__(self , private_key : rsa.RSAPrivateKey):
        self.private_key = private_key
        
    async def encode_jwt(
        self,
        payload: dict,
        algorithm: str = "RS256",
        expire_min: int = 30,
    ) -> str:
       
        try:
            to_encode = payload.copy()
            expire = datetime.now(timezone.utc) + timedelta(minutes=expire_min)
            to_encode.update({
                "exp": int(expire.timestamp()),
                "iat": int(datetime.now(timezone.utc).timestamp())
            })
            
            # Используем run_in_executor для асинхронности
            loop = asyncio.get_event_loop()
            encoded = await loop.run_in_executor(
                None,
                lambda: jwt.encode(
                    to_encode,
                    self.private_key,
                    algorithm=algorithm
                )
            )
            return encoded
            
        except Exception as e:
            logger.error(f'JWT encoding error: {e}', exc_info=True)
            raise JWTEncodeError(f'Encoding failed: {e}') from e
    

class JWTDecodeError(Exception):
    pass


class JWTDecoder:
    def __init__(self , public_key : rsa.RSAPublicKey):
        self.public_key = public_key


    async def decode_jwt(self , token : str, algorithms : list[str] = None):
        if algorithms is None:
            algorithms = ['RS256']
        try:
            decoded = await asyncio.to_thread(
                self._sync_decode, 
                token,
                algorithms,
                )
            return decoded
        
        except Exception as e:
            logger.error(f'Ошибка декодирования:{e}' , exc_info= True)
            raise JWTDecodeError(f'Не удалось обработать данные') from e
        
    # Вызов синхрнонной функции декодирования в отдельном потоке
    def _sync_decode(self, token : str , algorithms : list[str]) -> dict:
        return  jwt.decode(
            token, 
            self.public_key,
            algorithms=algorithms,
            options={"require": ["exp"]}
        )

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
