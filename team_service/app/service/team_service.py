"""
team_service.py
Слой бизнес-логики для Team Service.
"""
from fastapi import HTTPException
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
import httpx
import os

from app.models import TeamCreate, TeamUpdate, Team
from app.repository.team_repository import (
    create_team,
    update_team,
    delete_team,
    get_team_by_id,
    get_team_by_name,
    get_teams,
)
from app.external_services import verify_user_exists


# URL сервиса пользователей
USER_SERVICE_URL = os.getenv("USER_SERVICE_URL", "http://user_service:8001")


async def register_new_team(db: AsyncSession, team_data: TeamCreate) -> Team:
    """
    Регистрация новой команды. Проверяет имя команды и существование владельца.

    :param db: Асинхронная сессия SQLAlchemy.
    :param team_data: Данные для создания команды (имя, описание, владелец).
    :return: Созданная команда.
    :raises HTTPException: Если имя команды уже используется или владелец не существует.
    """
    # Проверяем, существует ли владелец команды
    await verify_user_exists(team_data.owner_id)

    # Проверяем, существует ли команда с таким же именем
    existing_team = await get_team_by_name(db, team_data.name)
    if existing_team:
        raise HTTPException(
            status_code=400, detail="Название команды уже используется"
        )

    db_team = await create_team(db, team_data)
    return Team.from_orm(db_team)


async def modify_team(
    db: AsyncSession, team_id: int, owner_id: int, team_data: TeamUpdate
) -> Optional[Team]:
    """
    Обновление команды по ID. Только владелец может редактировать.

    :param db: Асинхронная сессия SQLAlchemy.
    :param team_id: ID команды для обновления.
    :param owner_id: ID владельца команды.
    :param team_data: Новые данные для обновления команды.
    :return: Обновленная команда или None, если команда не найдена.
    :raises HTTPException: Если команда не найдена или пользователь не является владельцем.
    """
    db_team = await update_team(db, team_id, owner_id, team_data)
    return Team.from_orm(db_team) if db_team else None


async def remove_team(db: AsyncSession, team_id: int, owner_id: int) -> bool:
    """
    Удаление команды по ID. Только владелец может удалить команду.

    :param db: Асинхронная сессия SQLAlchemy.
    :param team_id: ID команды для удаления.
    :param owner_id: ID владельца команды.
    :return: True, если команда успешно удалена.
    :raises HTTPException: Если команда не найдена или пользователь не является владельцем.
    """
    return await delete_team(db, team_id, owner_id)


async def get_team_info(db: AsyncSession, team_id: int) -> Optional[Team]:
    """
    Получить информацию о команде по ID.

    :param db: Асинхронная сессия SQLAlchemy.
    :param team_id: ID команды для получения информации.
    :return: Данные команды или None, если команда не найдена.
    """
    db_team = await get_team_by_id(db, team_id)
    return Team.from_orm(db_team) if db_team else None


async def list_all_teams(db: AsyncSession) -> List[Team]:
    """
    Получить список всех команд.

    :param db: Асинхронная сессия SQLAlchemy.
    :return: Список всех команд.
    """
    db_teams = await get_teams(db)
    return [Team.from_orm(t) for t in db_teams]
