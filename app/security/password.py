from passlib.context import CryptContext
import bcrypt

from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def validate_password_strength(password: str) -> str:
    """
    Проверяет надежность пароля:
        Минимум 8 символов
        Как минимум одна заглавная буква
        Как минимум одна строчная буква
        Как минимум одна цифра
    """
    if len(password) < 8:
        raise ValueError("Пароль должен содержать не менее 8 символов")
    if not any(c.isupper() for c in password):
        raise ValueError("Пароль должен содержать хотя бы одну заглавную букву")
    if not any(c.islower() for c in password):
        raise ValueError("Пароль должен содержать хотя бы одну строчную букву")
    if not any(c.isdigit() for c in password):
        raise ValueError("Пароль должен содержать хотя бы одну цифру")
    return password


def get_password_hash(password: str) -> bytes:
    peppered_password = password + settings.PEPPER_SECRET

    hashed_password = bcrypt.hashpw(
        peppered_password.encode("utf-8"), bcrypt.gensalt(rounds=settings.BCRYPT_ROUNDS)
    )
    return hashed_password


def verify_password(input_password: str, hashed_password: str) -> bool:
    peppered_password = input_password + settings.PEPPER
    return bcrypt.checkpw(peppered_password.encode("utf-8"), hashed_password)
