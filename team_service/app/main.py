"""
main.py
Точка входа в User Service (FastAPI).
"""
import uvicorn
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.config import (
    POSTGRES_HOST,
    POSTGRES_PORT,
    POSTGRES_USER,
    POSTGRES_PASSWORD,
    POSTGRES_DB,
    USER_SERVICE_PORT,
)
from app.repository.user_repository import Base, DBUser
from app.models import UserCreate, UserUpdate
from app.service.user_service import (
    register_new_user,
    modify_user,
    remove_user,
    get_user_info,
    list_all_users
)

# ------------------------------------------------------------------------------
# Настройка подключения к БД
DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"

engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Инициализация таблиц (в реальном проекте использовать Alembic)
Base.metadata.create_all(bind=engine)


def get_db() -> Session:
    """
    Получение сессии для взаимодействия с БД.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
# ------------------------------------------------------------------------------


app = FastAPI(
    title="User Service",
    description="Сервис для управления пользователями",
    version="1.0.0"
)


@app.post("/users", summary="Регистрация нового пользователя")
def create_user_endpoint(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    Создает нового пользователя в системе.
    """
    return register_new_user(db, user_data)


@app.put("/users/{user_id}", summary="Обновление пользователя")
def update_user_endpoint(user_id: int, user_data: UserUpdate, db: Session = Depends(get_db)):
    """
    Обновляет данные пользователя по ID.
    """
    updated = modify_user(db, user_id, user_data)
    if not updated:
        raise HTTPException(status_code=404, detail="User not found")
    return updated


@app.delete("/users/{user_id}", summary="Удаление пользователя")
def delete_user_endpoint(user_id: int, db: Session = Depends(get_db)):
    """
    Удаляет пользователя по ID.
    """
    success = remove_user(db, user_id)
    if not success:
        raise HTTPException(status_code=404, detail="User not found")
    return {"detail": "User deleted successfully"}


@app.get("/users/{user_id}", summary="Получить информацию о пользователе")
def get_user_endpoint(user_id: int, db: Session = Depends(get_db)):
    """
    Возвращает информацию о пользователе по ID.
    """
    user = get_user_info(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@app.get("/users", summary="Список всех пользователей")
def list_users_endpoint(db: Session = Depends(get_db)):
    """
    Возвращает список всех пользователей.
    """
    return list_all_users(db)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=USER_SERVICE_PORT)
