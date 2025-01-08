"""
external_services.py
Модуль для взаимодействия с внешними сервисами.
"""
import os
from fastapi import HTTPException
import httpx

# URL из .env или значение по умолчанию
TEAM_SERVICE_URL = os.getenv("TEAM_SERVICE_URL", "http://team_service:8002")


async def verify_team_exists(team_id: int) -> None:
    """
    Проверяет, существует ли команда с данным ID в team_service.

    :param team_id: ID пользователя, которого нужно проверить.
    :raises HTTPException: Если команда с данным ID не найден.
    """
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{TEAM_SERVICE_URL}/teams/{team_id}")
        if response.status_code != 200:
            raise HTTPException(
                status_code=404, detail="Команда с указанным ID не найдена"
            )
