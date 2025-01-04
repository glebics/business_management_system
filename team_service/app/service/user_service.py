"""
user_service.py
Слой бизнес-логики для User Service.
"""
from typing import Optional, List
from sqlalchemy.orm import Session

from app.models import UserCreate, UserUpdate, User
from app.repository.user_repository import (
    create_user,
    update_user,
    delete_user,
    get_user_by_id,
    get_users
)


def register_new_user(db: Session, user_data: UserCreate) -> User:
    """
    Регистрация нового пользователя.
    Дополнительные проверки и логика могут быть добавлены здесь.
    """
    # Пример: проверить, что email не занят (реализовать по необходимости)
    db_user = create_user(db, user_data)
    return User.from_orm(db_user)


def modify_user(db: Session, user_id: int, user_data: UserUpdate) -> Optional[User]:
    """
    Обновление пользователя по ID.
    """
    db_user = update_user(db, user_id, user_data)
    if db_user:
        return User.from_orm(db_user)
    return None


def remove_user(db: Session, user_id: int) -> bool:
    """
    Удаление пользователя по ID.
    """
    return delete_user(db, user_id)


def get_user_info(db: Session, user_id: int) -> Optional[User]:
    """
    Получить информацию о пользователе по ID.
    """
    db_user = get_user_by_id(db, user_id)
    if db_user:
        return User.from_orm(db_user)
    return None


def list_all_users(db: Session) -> List[User]:
    """
    Получить список всех пользователей.
    """
    db_users = get_users(db)
    return [User.from_orm(u) for u in db_users]
