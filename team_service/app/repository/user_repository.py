"""
user_repository.py
Слой для работы с базой данных (CRUD-операции для пользователей).
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from datetime import datetime

# Импорт Pydantic-моделей
from app.models import UserCreate, UserUpdate, User

# Пример SQLAlchemy модели (упрощенно)
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class DBUser(Base):
    """
    SQLAlchemy модель для таблицы пользователей (пример).
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)
    full_name = Column(String, nullable=False)
    status = Column(String, nullable=False)
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


def create_user(db: Session, user_data: UserCreate) -> DBUser:
    """
    Создает пользователя в базе данных.
    """
    new_user = DBUser(
        email=user_data.email,
        password=user_data.password,  # Пароль должен быть захеширован
        full_name=user_data.full_name,
        status=user_data.status,
        team_id=user_data.team_id,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


def update_user(db: Session, user_id: int, user_data: UserUpdate) -> Optional[DBUser]:
    """
    Обновляет данные пользователя по ID.
    """
    user = db.query(DBUser).filter(DBUser.id == user_id).first()
    if not user:
        return None
    if user_data.email is not None:
        user.email = user_data.email
    if user_data.full_name is not None:
        user.full_name = user_data.full_name
    if user_data.status is not None:
        user.status = user_data.status
    if user_data.team_id is not None:
        user.team_id = user_data.team_id
    db.commit()
    db.refresh(user)
    return user


def delete_user(db: Session, user_id: int) -> bool:
    """
    Удаляет пользователя из базы данных.
    """
    user = db.query(DBUser).filter(DBUser.id == user_id).first()
    if not user:
        return False
    db.delete(user)
    db.commit()
    return True


def get_user_by_id(db: Session, user_id: int) -> Optional[DBUser]:
    """
    Возвращает пользователя по ID.
    """
    return db.query(DBUser).filter(DBUser.id == user_id).first()


def get_users(db: Session) -> List[DBUser]:
    """
    Возвращает всех пользователей.
    """
    return db.query(DBUser).all()
