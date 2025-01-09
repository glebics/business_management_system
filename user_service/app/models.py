# user_service/app/models.py

"""
models.py
Pydantic-модели для User Service.
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
    role: str = "member"  # По умолчанию "member"


class UserCreate(UserBase):
    """
    Модель для создания нового пользователя.
    """
    password: str
    # Пользователь может выбрать команду при регистрации
    team_id: Optional[int] = None


class UserUpdate(BaseModel):
    """
    Модель для обновления данных пользователя.
    """
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    status: Optional[str] = None
    role: Optional[str] = "member"  # По умолчанию "member"
    team_id: Optional[int] = None


class User(UserBase):
    """
    Модель для возврата информации о пользователе.
    """
    id: int
    team_id: Optional[int]
    created_at: datetime

    class Config:
        orm_mode = True


class LoginRequest(BaseModel):
    """
    Модель для запроса на вход.
    """
    email: EmailStr
    password: str
