# team_service/app/models.py

"""
models.py
Pydantic-модели для валидации данных в Team Service.
"""
from pydantic import BaseModel
from typing import Optional


class TeamBase(BaseModel):
    """
    Общие поля для команды.
    """
    name: str
    description: Optional[str] = None


class TeamCreate(TeamBase):
    """
    Модель для создания новой команды.
    """
    pass  # Наследует все поля от TeamBase


class TeamUpdate(BaseModel):
    """
    Модель для обновления данных команды.
    """
    name: Optional[str] = None
    description: Optional[str] = None


class Team(TeamBase):
    """
    Модель для возврата информации о команде.
    """
    id: int

    class Config:
        orm_mode = True
