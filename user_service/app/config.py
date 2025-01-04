"""
config.py
Загрузка переменных окружения из .dev.env
и объявление глобальных констант для user_service.
"""
import os
from dotenv import load_dotenv

# Путь к файлу окружения (из корня проекта)
ENV_PATH = os.path.join(os.path.dirname(__file__), "../../.dev.env")
load_dotenv(dotenv_path=ENV_PATH)

POSTGRES_HOST: str = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT: int = int(os.getenv("POSTGRES_PORT", "5432"))
POSTGRES_USER: str = os.getenv("POSTGRES_USER", "postgres")
POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "postgres")
POSTGRES_DB: str = os.getenv("POSTGRES_DB", "business_db")

USER_SERVICE_PORT: int = int(os.getenv("USER_SERVICE_PORT", "8001"))

SECRET_KEY: str = os.getenv("SECRET_KEY", "supersecretkey")
ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES: int = int(
    os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))
