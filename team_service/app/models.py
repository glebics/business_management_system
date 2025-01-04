"""
models.py
Pydantic-модели для валидации данных в User Service.
"""
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class UserBase(BaseModel):
    """
    Общие поля для пользователя.
    """
    email: EmailStr
    full_name: str
    status: str


class UserCreate(UserBase):
    """
    Модель для создания нового пользователя.
    """
    password: str
    team_id: Optional[int] = None


class UserUpdate(BaseModel):
    """
    Модель для обновления данных пользователя.
    """
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    status: Optional[str] = None
    team_id: Optional[int] = None


class UserDelete(BaseModel):
    """
    Модель для удаления пользователя (если нужно что-то специфическое).
    """
    user_id: int


class User(UserBase):
    """
    Модель для возврата информации о пользователе.
    """
    id: int
    team_id: Optional[int]
    created_at: datetime

    class Config:
        orm_mode = True
