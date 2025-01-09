# team_service/app/main.py
"""
main.py
Точка входа в Team Service (FastAPI).
"""
import uvicorn
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from typing import List

from app.config import (
    POSTGRES_HOST,
    POSTGRES_PORT,
    POSTGRES_USER,
    POSTGRES_PASSWORD,
    POSTGRES_DB,
    TEAM_SERVICE_PORT,
)
from app.repository.team_repository import Base, DBTeam
from app.models import TeamCreate, TeamUpdate, Team
from app.service.team_service import (
    register_new_team,
    modify_team,
    remove_team,
    get_team_info,
    list_all_teams
)
from app.external_services import verify_token  # Импорт проверки токена

app = FastAPI(
    title="Team Service",
    description="Сервис для управления командами",
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


@app.post("/teams", summary="Создать новую команду", response_model=Team)
async def create_team_endpoint(
    team_data: TeamCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(verify_token)
):
    """
    Создает новую команду (только авторизованные пользователи).
    """
    return await register_new_team(db, team_data)


@app.put("/teams/{team_id}", summary="Обновить команду", response_model=Team)
async def update_team_endpoint(
    team_id: int,
    owner_id: int,
    team_data: TeamUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(verify_token)
):
    """
    Обновляет команду (только владелец может вносить изменения, доступ только для авторизованных пользователей).
    """
    updated = await modify_team(db, team_id, owner_id, team_data)
    if not updated:
        raise HTTPException(status_code=404, detail="Команда не найдена")
    return updated


@app.delete("/teams/{team_id}", summary="Удалить команду")
async def delete_team_endpoint(
    team_id: int,
    owner_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(verify_token)
):
    """
    Удаляет команду (только владелец может удалить, доступ только для авторизованных пользователей).
    """
    success = await remove_team(db, team_id, owner_id)
    if not success:
        raise HTTPException(status_code=404, detail="Команда не найдена")
    return {"detail": "Команда успешно удалена"}


@app.get("/teams/{team_id}", summary="Получить информацию о команде", response_model=Team)
async def get_team_endpoint(
    team_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(verify_token)
):
    """
    Возвращает информацию о команде по ID (доступ только для авторизованных пользователей).
    """
    team = await get_team_info(db, team_id)
    if not team:
        raise HTTPException(status_code=404, detail="Команда не найдена")
    return team


@app.get("/teams", summary="Список всех команд", response_model=List[Team])
async def list_teams_endpoint(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(verify_token)
):
    """
    Возвращает список всех команд (доступ только для авторизованных пользователей).
    """
    return await list_all_teams(db)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=TEAM_SERVICE_PORT)
