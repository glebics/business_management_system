# user_service/app/auth.py

"""
auth.py
Модуль для работы с аутентификацией (JWT, хэширование паролей).
"""

from jose import jwt
from datetime import datetime, timedelta
from passlib.context import CryptContext
from app.config import SECRET_KEY, ALGORITHM

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """
    Хэширует пароль с использованием bcrypt.

    :param password: Оригинальный пароль.
    :return: Хэшированный пароль.
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Проверяет соответствие введенного пароля и хэшированного.

    :param plain_password: Введенный пароль.
    :param hashed_password: Хэшированный пароль из БД.
    :return: True, если пароли совпадают, иначе False.
    """
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: timedelta) -> str:
    """
    Генерирует JWT-токен.

    - Кодирует переданные данные (`data`) в JWT-формате.
    - Устанавливает время истечения токена.

    :param data: Данные, которые будут закодированы в JWT.
    :param expires_delta: Время жизни токена.
    :return: Закодированный JWT-токен.
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
