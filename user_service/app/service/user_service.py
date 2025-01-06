# user_service/app/service/user_service.py

"""
user_service.py
Слой бизнес-логики для User Service.
"""
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
    get_user_by_email,
)


async def hash_password(password: str) -> str:
    """
    Хэширует пароль с использованием bcrypt.
    """
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


async def register_new_user(db: AsyncSession, user_data: UserCreate) -> User:
    """
    Регистрация нового пользователя.
    Проверяет, не занят ли email, затем хэширует пароль перед сохранением.
    """
    # Проверяем, не занят ли email
    existing_user = await get_user_by_email(db, user_data.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="Email уже используется")

    # Хэшируем пароль перед сохранением
    hashed_password = await hash_password(user_data.password)
    user_data.password = hashed_password  # Заменяем пароль на хэш

    # Создаем пользователя в БД
    db_user = await create_user(db, user_data)
    return User.from_orm(db_user)


async def modify_user(db: AsyncSession, user_id: int, user_data: UserUpdate) -> Optional[User]:
    """
    Обновление пользователя по ID.
    """
    db_user = await update_user(db, user_id, user_data)
    if db_user:
        return User.from_orm(db_user)
    return None


async def remove_user(db: AsyncSession, user_id: int) -> bool:
    """
    Удаление пользователя по ID.
    """
    return await delete_user(db, user_id)


async def get_user_info(db: AsyncSession, user_id: int) -> Optional[User]:
    """
    Получить информацию о пользователе по ID.
    """
    db_user = await get_user_by_id(db, user_id)
    if db_user:
        return User.from_orm(db_user)
    return None


async def list_all_users(db: AsyncSession) -> List[User]:
    """
    Получить список всех пользователей.
    """
    db_users = await get_users(db)
    return [User.from_orm(u) for u in db_users]
