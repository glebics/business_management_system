# user_service/app/service/user_service.py

"""
user_service.py
Слой бизнес-логики для User Service.
"""
from app.config import ACCESS_TOKEN_EXPIRE_MINUTES
from app.auth import hash_password, verify_password, create_access_token
from datetime import timedelta
from fastapi import HTTPException, Depends
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
    Регистрирует нового пользователя.

    - Проверяет, существует ли уже пользователь с указанным email.
    - Хэширует пароль перед сохранением.
    - Создает запись в базе данных.

    :param db: Асинхронная сессия SQLAlchemy.
    :param user_data: Данные нового пользователя (email, пароль, имя, статус, роль).
    :return: Зарегистрированный пользователь.
    :raises HTTPException: 400 - если email уже используется.
    """
    existing_user = await get_user_by_email(db, user_data.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="Email уже используется")

    user_data.password = hash_password(user_data.password)
    db_user = await create_user(db, user_data)
    return User.from_orm(db_user)


async def authenticate_user(db: AsyncSession, email: str, password: str) -> User:
    """
    Аутентифицирует пользователя по email и паролю.

    - Проверяет, существует ли пользователь с таким email.
    - Сравнивает введенный пароль с хэшированным в базе данных.

    :param db: Асинхронная сессия SQLAlchemy.
    :param email: Email пользователя.
    :param password: Введенный пароль.
    :return: Объект пользователя, если аутентификация успешна.
    :raises HTTPException: 401 - если email или пароль неверные.
    """
    user = await get_user_by_email(db, email)
    if not user or not verify_password(password, user.password):
        raise HTTPException(status_code=401, detail="Неверные учетные данные")

    return user


async def login_user(db: AsyncSession, email: str, password: str) -> dict[str, str]:
    """
    Логин пользователя и генерация JWT-токена.

    - Аутентифицирует пользователя с помощью `authenticate_user`.
    - Генерирует JWT-токен с истечением времени `ACCESS_TOKEN_EXPIRE_MINUTES`.

    :param db: Асинхронная сессия SQLAlchemy.
    :param email: Email пользователя.
    :param password: Введенный пароль.
    :return: Словарь с JWT-токеном и его типом (`access_token`, `token_type`).
    """
    user = await authenticate_user(db, email, password)
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires)

    return {"access_token": access_token, "token_type": "bearer"}


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


async def modify_user(db: AsyncSession, user_id: int, user_data: UserUpdate) -> Optional[User]:
    """
    Обновляет данные пользователя по ID.

    - Проверяет, существует ли пользователь.
    - Обновляет поля, если они указаны.

    :param db: Асинхронная сессия SQLAlchemy.
    :param user_id: ID пользователя.
    :param user_data: Данные для обновления.
    :return: Обновленный пользователь или None.
    """
    db_user = await update_user(db, user_id, user_data)
    if db_user:
        return User.from_orm(db_user)
    return None


async def remove_user(db: AsyncSession, user_id: int, current_user: User) -> bool:
    """
    Удаляет пользователя по ID.

    - Проверяет, что текущий пользователь может удалить только свой аккаунт.
    - Проверяет, существует ли пользователь.
    - Удаляет пользователя из базы данных.

    :param db: Асинхронная сессия SQLAlchemy.
    :param user_id: ID пользователя для удаления.
    :param current_user: Текущий аутентифицированный пользователь.
    :return: True, если пользователь успешно удален, иначе False.
    :raises HTTPException: 403 - если пользователь пытается удалить чужой аккаунт.
    """
    if user_id != current_user.id:
        raise HTTPException(
            status_code=403, detail="Вы можете удалить только свой аккаунт."
        )

    return await delete_user(db, user_id)


async def get_user_info(db: AsyncSession, user_id: int) -> Optional[User]:
    """
    Получает информацию о пользователе по ID.

    - Проверяет, существует ли пользователь в базе данных.
    - Возвращает объект пользователя, если он найден.

    :param db: Асинхронная сессия SQLAlchemy.
    :param user_id: ID пользователя для поиска.
    :return: Объект пользователя или None, если пользователь не найден.
    :raises HTTPException: 404 - если пользователь не найден.
    """
    db_user = await get_user_by_id(db, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    return User.from_orm(db_user)


async def list_all_users(db: AsyncSession) -> List[User]:
    """
    Возвращает список всех пользователей в системе.

    - Извлекает всех пользователей из базы данных.
    - Преобразует записи базы данных в объекты модели User.

    :param db: Асинхронная сессия SQLAlchemy.
    :return: Список объектов модели User.
    """
    db_users = await get_users(db)
    return [User.from_orm(user) for user in db_users]
