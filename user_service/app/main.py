# user_service/app/main.py

"""
main.py
Точка входа в User Service (FastAPI).
"""
import uvicorn
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
from typing import List

from app.config import (
    POSTGRES_HOST,
    POSTGRES_PORT,
    POSTGRES_USER,
    POSTGRES_PASSWORD,
    POSTGRES_DB,
    USER_SERVICE_PORT,
)
from app.repository.user_repository import Base, DBUser
from app.models import UserCreate, UserUpdate, UserDelete, User
from app.service.user_service import (
    register_new_user,
    modify_user,
    remove_user,
    get_user_info,
    list_all_users,
    add_user_to_team,
    remove_user_from_team,
    list_team_members,
)

app = FastAPI(
    title="User Service",
    description="Сервис для управления пользователями",
    version="1.0.0"
)

# ------------------------------------------------------------------------------
# Настройка подключения к БД (Асинхронная)
DATABASE_URL = f"postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"

engine = create_async_engine(DATABASE_URL, echo=False)
AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)


async def init_models():
    """
    Инициализация таблиц в базе данных.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


@app.on_event("startup")
async def on_startup():
    """
    Действия при запуске приложения.
    """
    await init_models()


async def get_db() -> AsyncSession:
    """
    Получение сессии для взаимодействия с БД.
    """
    async with AsyncSessionLocal() as session:
        yield session
# ------------------------------------------------------------------------------


@app.post("/users", summary="Регистрация нового пользователя", response_model=User)
async def create_user_endpoint(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    """
    Создает нового пользователя в системе.
    """
    return await register_new_user(db, user_data)


@app.put("/users/{user_id}", summary="Обновление пользователя", response_model=User)
async def update_user_endpoint(user_id: int, user_data: UserUpdate, db: AsyncSession = Depends(get_db)):
    """
    Обновляет данные пользователя по ID.
    """
    updated = await modify_user(db, user_id, user_data)
    if not updated:
        raise HTTPException(status_code=404, detail="User not found")
    return updated


@app.delete("/users/{user_id}", summary="Удаление пользователя")
async def delete_user_endpoint(user_id: int, db: AsyncSession = Depends(get_db)):
    """
    Удаляет пользователя по ID.
    """
    success = await remove_user(db, user_id)
    if not success:
        raise HTTPException(status_code=404, detail="User not found")
    return {"detail": "User deleted successfully"}


@app.get("/users/{user_id}", summary="Получить информацию о пользователе", response_model=User)
async def get_user_endpoint(user_id: int, db: AsyncSession = Depends(get_db)):
    """
    Возвращает информацию о пользователе по ID.
    """
    user = await get_user_info(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@app.get("/users", summary="Список всех пользователей", response_model=List[User])
async def list_users_endpoint(db: AsyncSession = Depends(get_db)):
    """
    Возвращает список всех пользователей.
    """
    return await list_all_users(db)


@app.post("/teams/{team_id}/add_user", summary="Добавить пользователя в команду")
async def add_user_to_team_endpoint(
    team_id: int, user_id: int, admin_id: int, db: AsyncSession = Depends(get_db)
):
    """
    Администратор добавляет пользователя в команду.
    """
    return await add_user_to_team(db, admin_id, user_id, team_id)


@app.post("/teams/{team_id}/remove_user", summary="Удалить пользователя из команды")
async def remove_user_from_team_endpoint(
    user_id: int, admin_id: int, db: AsyncSession = Depends(get_db)
):
    """
    Администратор удаляет пользователя из команды.
    """
    return await remove_user_from_team(db, admin_id, user_id)


@app.get("/teams/{team_id}/members", summary="Получить список участников команды")
async def list_team_members_endpoint(team_id: int, db: AsyncSession = Depends(get_db)):
    """
    Возвращает список всех пользователей, входящих в команду.
    """
    return await list_team_members(db, team_id)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=USER_SERVICE_PORT)
