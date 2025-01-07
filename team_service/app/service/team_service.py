# team_service/app/service/team_service.py

"""
team_service.py
Слой бизнес-логики для Team Service.
"""
from fastapi import HTTPException
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import TeamCreate, TeamUpdate, Team
from app.repository.team_repository import (
    create_team,
    update_team,
    delete_team,
    get_team_by_id,
    get_team_by_name,
    get_teams,
)


async def register_new_team(db: AsyncSession, team_data: TeamCreate) -> Team:
    """
    Регистрация новой команды. Проверяет имя, затем создает команду.
    """
    existing_team = await get_team_by_name(db, team_data.name)
    if existing_team:
        raise HTTPException(
            status_code=400, detail="Название команды уже используется")

    db_team = await create_team(db, team_data)
    return Team.from_orm(db_team)


async def modify_team(db: AsyncSession, team_id: int, owner_id: int, team_data: TeamUpdate) -> Optional[Team]:
    """
    Обновление команды по ID. Только владелец может редактировать.
    """
    db_team = await update_team(db, team_id, owner_id, team_data)
    return Team.from_orm(db_team) if db_team else None


async def remove_team(db: AsyncSession, team_id: int, owner_id: int) -> bool:
    """
    Удаление команды по ID. Только владелец может удалить команду.
    """
    return await delete_team(db, team_id, owner_id)


async def get_team_info(db: AsyncSession, team_id: int) -> Optional[Team]:
    """
    Получить информацию о команде по ID.
    """
    db_team = await get_team_by_id(db, team_id)
    return Team.from_orm(db_team) if db_team else None


async def list_all_teams(db: AsyncSession) -> List[Team]:
    """
    Получить список всех команд.
    """
    db_teams = await get_teams(db)
    return [Team.from_orm(t) for t in db_teams]
