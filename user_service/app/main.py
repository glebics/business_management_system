# user_service/app/main.py

"""
main.py
Точка входа в User Service (FastAPI).
"""

import uvicorn
from fastapi import FastAPI, Depends, HTTPException, Security
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from typing import List

from app.config import (
    POSTGRES_HOST, POSTGRES_PORT, POSTGRES_USER, POSTGRES_PASSWORD,
    POSTGRES_DB, USER_SERVICE_PORT, SECRET_KEY, ALGORITHM
)
from app.repository.user_repository import Base, DBUser
from app.models import UserCreate, UserUpdate, User, LoginRequest
from app.service.user_service import (
    register_new_user, modify_user, remove_user, get_user_info,
    list_all_users, login_user, authenticate_user,
    add_user_to_team, remove_user_from_team, list_team_members
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
    bind=engine, class_=AsyncSession, expire_on_commit=False)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")


async def init_models():
    """Инициализация таблиц в базе данных."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


@app.on_event("startup")
async def on_startup():
    """Действия при запуске приложения."""
    await init_models()


async def get_db() -> AsyncSession:
    """Получение сессии для взаимодействия с БД."""
    async with AsyncSessionLocal() as session:
        yield session


async def get_current_user(token: str = Security(oauth2_scheme), db: AsyncSession = Depends(get_db)) -> User:
    """
    Получает текущего пользователя по JWT-токену.

    :param token: JWT-токен пользователя.
    :param db: Асинхронная сессия базы данных.
    :return: Данные аутентифицированного пользователя.
    :raises HTTPException: 401 - если токен недействителен.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if not email:
            raise HTTPException(
                status_code=401, detail="Недействительный токен")

        user = await authenticate_user(db, email, "")
        return user
    except JWTError:
        raise HTTPException(status_code=401, detail="Недействительный токен")


# ------------------------ ЭНДПОИНТЫ АВТОРИЗАЦИИ ------------------------
@app.post("/login", summary="Авторизация пользователя")
async def login_endpoint(login_data: LoginRequest, db: AsyncSession = Depends(get_db)):
    """
    Логин пользователя, возвращает JWT-токен.

    :param login_data: Данные для входа (email, пароль).
    :param db: Асинхронная сессия базы данных.
    :return: JWT-токен.
    """
    return await login_user(db, login_data.email, login_data.password)


# ------------------------ ЭНДПОИНТЫ ПОЛЬЗОВАТЕЛЕЙ ------------------------
@app.post("/users", summary="Регистрация нового пользователя", response_model=User)
async def create_user_endpoint(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    """
    Создает нового пользователя в системе.

    :param user_data: Данные нового пользователя.
    :param db: Асинхронная сессия базы данных.
    :return: Созданный пользователь.
    """
    return await register_new_user(db, user_data)


@app.put("/users/{user_id}", summary="Обновление пользователя", response_model=User)
async def update_user_endpoint(
    user_id: int, user_data: UserUpdate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)
):
    """
    Обновляет данные пользователя по ID (только если текущий пользователь - владелец профиля).

    :param user_id: ID обновляемого пользователя.
    :param user_data: Новые данные.
    :param db: Асинхронная сессия базы данных.
    :param current_user: Авторизованный пользователь.
    :return: Обновленный пользователь.
    """
    if current_user.id != user_id:
        raise HTTPException(
            status_code=403, detail="Вы можете обновлять только свой профиль")

    updated = await modify_user(db, user_id, user_data)
    if not updated:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    return updated


@app.delete("/users/{user_id}", summary="Удаление пользователя")
async def delete_user_endpoint(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Удаляет пользователя по ID, если это его аккаунт.

    :param user_id: ID пользователя.
    :param db: Асинхронная сессия базы данных.
    :param current_user: Текущий аутентифицированный пользователь.
    :return: Подтверждение успешного удаления.
    """
    success = await remove_user(db, user_id, current_user)
    if not success:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    return {"detail": "Пользователь успешно удален"}


@app.get("/users/{user_id}", summary="Получить информацию о пользователе", response_model=User)
async def get_user_endpoint(user_id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Возвращает информацию о пользователе по ID.

    :param user_id: ID пользователя.
    :param db: Асинхронная сессия базы данных.
    :param current_user: Авторизованный пользователь.
    :return: Данные пользователя.
    """
    user = await get_user_info(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    return user


@app.get("/users", summary="Список всех пользователей", response_model=List[User])
async def list_users_endpoint(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Возвращает список всех пользователей.

    :param db: Асинхронная сессия базы данных.
    :param current_user: Авторизованный пользователь.
    :return: Список пользователей.
    """
    return await list_all_users(db)


# ------------------------ ЭНДПОИНТЫ КОМАНД ------------------------
@app.post("/teams/{team_id}/add_user", summary="Добавить пользователя в команду")
async def add_user_to_team_endpoint(team_id: int, user_id: int, admin_id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Администратор добавляет пользователя в команду.

    :param team_id: ID команды.
    :param user_id: ID пользователя.
    :param admin_id: ID администратора.
    :param db: Асинхронная сессия базы данных.
    :param current_user: Авторизованный пользователь.
    :return: Подтверждение добавления.
    """
    return await add_user_to_team(db, admin_id, user_id, team_id)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=USER_SERVICE_PORT)
