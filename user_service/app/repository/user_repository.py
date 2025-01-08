# user_service/app/repository/user_repository.py

"""
user_repository.py
Слой для работы с базой данных (CRUD-операции для пользователей).
"""
from typing import List, Optional
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.future import select
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from app.models import UserCreate, UserUpdate, User

Base = declarative_base()


class DBUser(Base):
    """
    SQLAlchemy модель для пользователей.
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)
    full_name = Column(String, nullable=False)
    status = Column(String, nullable=False)
    # "member" или "admin"
    role = Column(String, nullable=False, default="member")
    team_id = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


async def list_team_members(db: AsyncSession, team_id: int) -> List[User]:
    """
    Получает список всех пользователей в команде.
    """
    result = await db.execute(select(User).where(User.team_id == team_id))
    users = result.scalars().all()

    if not users:
        raise HTTPException(status_code=404, detail="В команде нет участников")

    return [User.from_orm(user) for user in users]


async def get_user_by_email(db: AsyncSession, email: str) -> Optional[DBUser]:
    """
    Возвращает пользователя по email, если он существует.
    """
    result = await db.execute(select(DBUser).where(DBUser.email == email))
    return result.scalars().first()


async def create_user(db: AsyncSession, user_data: UserCreate) -> DBUser:
    """
    Создает пользователя в базе данных.
    """
    new_user = DBUser(
        email=user_data.email,
        password=user_data.password,
        full_name=user_data.full_name,
        status=user_data.status,
        role=user_data.role,
        team_id=user_data.team_id,
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user


async def update_user(db: AsyncSession, user_id: int, user_data: UserUpdate) -> Optional[DBUser]:
    """
    Обновляет данные пользователя по ID.
    """
    result = await db.execute(select(DBUser).where(DBUser.id == user_id))
    user = result.scalars().first()
    if not user:
        return None

    if user_data.email is not None:
        user.email = user_data.email
    if user_data.full_name is not None:
        user.full_name = user_data.full_name
    if user_data.status is not None:
        user.status = user_data.status
    if user_data.role is not None:
        user.role = user_data.role
    if user_data.team_id is not None:
        user.team_id = user_data.team_id

    await db.commit()
    await db.refresh(user)
    return user


async def delete_user(db: AsyncSession, user_id: int) -> bool:
    """
    Удаляет пользователя из базы данных.
    """
    result = await db.execute(select(DBUser).where(DBUser.id == user_id))
    user = result.scalars().first()
    if not user:
        return False
    await db.delete(user)
    await db.commit()
    return True


async def get_user_by_id(db: AsyncSession, user_id: int) -> Optional[DBUser]:
    """
    Возвращает пользователя по ID.
    """
    result = await db.execute(select(DBUser).where(DBUser.id == user_id))
    return result.scalars().first()


async def get_users(db: AsyncSession) -> List[DBUser]:
    """
    Возвращает всех пользователей.
    """
    result = await db.execute(select(DBUser))
    return result.scalars().all()


async def get_users_by_team(db: AsyncSession, team_id: int) -> List[DBUser]:
    """
    Возвращает всех пользователей, состоящих в определенной команде.
    """
    result = await db.execute(select(DBUser).where(DBUser.team_id == team_id))
    return result.scalars().all()
