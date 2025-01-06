# user_service/app/service/user_service.py

"""
user_service.py
Слой бизнес-логики для User Service.
"""
import httpx
from fastapi import HTTPException
import bcrypt
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import UserCreate, UserUpdate, User
from app.repository.user_repository import (
    create_user,
    update_user,
    delete_user,
    get_user_by_id,
    get_users,
    get_users_by_team,
    get_user_by_email,
)


async def hash_password(password: str) -> str:
    """
    Хэширует пароль с использованием bcrypt.
    """
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


async def check_team_exists(team_id: int) -> bool:
    """
    Отправляет запрос в team_service, чтобы проверить, существует ли команда.
    """
    TEAM_SERVICE_URL = "http://team_service:8002"

    async with httpx.AsyncClient() as client:
        response = await client.get(f"{TEAM_SERVICE_URL}/teams/{team_id}")

    return response.status_code == 200  # Если 200, команда существует


async def register_new_user(db: AsyncSession, user_data: UserCreate) -> User:
    """
    Регистрация нового пользователя. Проверяет email, хэширует пароль,
    проверяет существование команды.
    """
    existing_user = await get_user_by_email(db, user_data.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="Email уже используется")

    hashed_password = await hash_password(user_data.password)
    user_data.password = hashed_password

    if user_data.team_id:
        team_exists = await check_team_exists(user_data.team_id)
        if not team_exists:
            raise HTTPException(status_code=400, detail="Команда не найдена")

    db_user = await create_user(db, user_data)
    return User.from_orm(db_user)


async def add_user_to_team(db: AsyncSession, admin_id: int, user_id: int, team_id: int) -> bool:
    """
    Администратор добавляет пользователя в команду.
    """
    admin = await get_user_by_id(db, admin_id)
    if not admin or admin.role != "admin":
        raise HTTPException(
            status_code=403, detail="Только администратор может добавлять пользователей")

    user = await get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    if user.team_id is not None:
        raise HTTPException(
            status_code=400, detail="Пользователь уже состоит в команде")

    user.team_id = team_id
    await db.commit()
    await db.refresh(user)
    return True


async def remove_user_from_team(db: AsyncSession, admin_id: int, user_id: int) -> bool:
    """
    Администратор удаляет пользователя из команды.
    """
    admin = await get_user_by_id(db, admin_id)
    if not admin or admin.role != "admin":
        raise HTTPException(
            status_code=403, detail="Только администратор может удалять пользователей")

    user = await get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    if user.team_id is None:
        raise HTTPException(
            status_code=400, detail="Пользователь не состоит в команде")

    user.team_id = None
    await db.commit()
    await db.refresh(user)
    return True


async def list_team_members(db: AsyncSession, team_id: int) -> List[User]:
    """
    Возвращает список всех пользователей, входящих в команду.
    """
    db_users = await get_users_by_team(db, team_id)
    return [User.from_orm(user) for user in db_users]
