# team_service/external_services.py
"""
Модуль для взаимодействия с внешними сервисами.
"""
import os
from fastapi import HTTPException, Security, Depends
from fastapi.security import OAuth2PasswordBearer
import httpx
from jose import jwt
# Импортируем секретный ключ и алгоритм
from app.config import SECRET_KEY, ALGORITHM

# URL из .env или значение по умолчанию
USER_SERVICE_URL = os.getenv("USER_SERVICE_URL", "http://user_service:8001")

# Определяем схему OAuth2
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")  # Убираем USER_SERVICE_URL


async def verify_user_exists(user_id: int) -> None:
    """
    Проверяет, существует ли пользователь с данным ID в user_service.

    :param user_id: ID пользователя, которого нужно проверить.
    :raises HTTPException: Если пользователь с данным ID не найден.
    """
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{USER_SERVICE_URL}/users/{user_id}")
        if response.status_code != 200:
            raise HTTPException(
                status_code=404, detail="Пользователь с указанным ID не найден"
            )


async def verify_token(token: str = Security(oauth2_scheme)):
    """
    Проверяет валидность JWT-токена, запрашивая информацию о пользователе из user_service.
    """
    if not token:
        raise HTTPException(status_code=401, detail="Токен отсутствует")

    try:
        # Декодируем токен локально
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")

        if not email:
            raise HTTPException(
                status_code=401, detail="Недействительный токен")

        # Проверяем, существует ли пользователь в user_service
        headers = {"Authorization": f"Bearer {token}"}
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{USER_SERVICE_URL}/users/me", headers=headers)

        if response.status_code == 422:
            raise HTTPException(
                status_code=422, detail="Некорректный токен. Проверьте заголовок Authorization.")

        if response.status_code != 200:
            raise HTTPException(
                status_code=401, detail="Недействительный токен")

        return response.json()  # Возвращаем данные пользователя

    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Недействительный токен")
