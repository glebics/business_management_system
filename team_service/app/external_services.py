"""
external_services.py
Модуль для взаимодействия с внешними сервисами.
"""
import os
from fastapi import HTTPException
import httpx

# URL из .env или значение по умолчанию
USER_SERVICE_URL = os.getenv("USER_SERVICE_URL", "http://user_service:8001")


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
