#!/usr/bin/env bash

echo "⏳ Ожидание готовности PostgreSQL..."

# Проверяем доступность базы данных
until pg_isready -h "$POSTGRES_HOST" -p "$POSTGRES_PORT" -U "$POSTGRES_USER"; do
    echo "💤 PostgreSQL пока не готов, ждем..."
    sleep 2
done

echo "✅ PostgreSQL готов! Запускаем Team Service..."

exec uvicorn app.main:app --host 0.0.0.0 --port 8002
