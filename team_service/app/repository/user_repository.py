# team_service/app/repository/team_repository.py

"""
team_repository.py
Слой для работы с базой данных (CRUD-операции для команд).
"""
from typing import List, Optional
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import Column, Integer, String
from sqlalchemy.future import select
from sqlalchemy.ext.declarative import declarative_base

from app.models import TeamCreate, TeamUpdate

Base = declarative_base()


class DBTeam(Base):
    """
    SQLAlchemy модель для таблицы команд.
    """
    __tablename__ = "teams"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)


async def get_team_by_name(db: AsyncSession, name: str) -> DBTeam | None:
    """
    Проверяет, существует ли уже команда с данным именем.
    """
    result = await db.execute(select(DBTeam).where(DBTeam.name == name))
    return result.scalars().first()


async def create_team(db: AsyncSession, team_data: TeamCreate) -> DBTeam:
    """
    Создает команду в базе данных.
    """
    new_team = DBTeam(
        name=team_data.name,
        description=team_data.description,
    )
    db.add(new_team)
    await db.commit()
    await db.refresh(new_team)
    return new_team


async def update_team(db: AsyncSession, team_id: int, user_id: int, team_data: TeamUpdate) -> Optional[DBTeam]:
    """
    Обновляет данные команды. Только владелец может вносить изменения.
    """
    result = await db.execute(select(DBTeam).where(DBTeam.id == team_id))
    team = result.scalars().first()

    if not team:
        raise HTTPException(status_code=404, detail="Команда не найдена")

    if team.owner_id != user_id:
        raise HTTPException(
            status_code=403, detail="Вы не владелец этой команды")

    if team_data.name is not None:
        team.name = team_data.name
    if team_data.description is not None:
        team.description = team_data.description

    await db.commit()
    await db.refresh(team)
    return team


async def remove_team(db: AsyncSession, team_id: int, user_id: int) -> bool:
    """
    Удаление команды по ID. Проверяет, является ли пользователь владельцем.
    """
    result = await db.execute(select(DBTeam).where(DBTeam.id == team_id))
    team = result.scalars().first()

    if not team:
        raise HTTPException(status_code=404, detail="Команда не найдена")

    if team.owner_id != user_id:
        raise HTTPException(
            status_code=403, detail="Вы не владелец этой команды")

    await db.delete(team)
    await db.commit()
    return True


"""
старая версия удаления
async def delete_team(db: AsyncSession, team_id: int) -> bool:
    "" "
    Удаляет команду из базы данных.
    "" "
    result = await db.execute(select(DBTeam).where(DBTeam.id == team_id))
    team = result.scalars().first()
    if not team:
        return False
    await db.delete(team)
    await db.commit()
    return True
"""


async def get_team_by_id(db: AsyncSession, team_id: int) -> Optional[DBTeam]:
    """
    Возвращает команду по ID.
    """
    result = await db.execute(select(DBTeam).where(DBTeam.id == team_id))
    return result.scalars().first()


async def get_teams(db: AsyncSession) -> List[DBTeam]:
    """
    Возвращает все команды.
    """
    result = await db.execute(select(DBTeam))
    return result.scalars().all()
