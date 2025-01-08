#!/usr/bin/env bash

echo "Проверка готовности Team Service..."

# Попробуем несколько раз сделать запрос к БД и проверить наличие таблицы "teams"
for i in {1..30}; do
    TABLE_EXISTS=$(psql "host=$POSTGRES_HOST port=$POSTGRES_PORT user=$POSTGRES_USER password=$POSTGRES_PASSWORD dbname=$POSTGRES_DB" \
        -tAc "SELECT to_regclass('public.teams');")
    if [ "$TABLE_EXISTS" = "teams" ]; then
        echo "Таблица 'teams' найдена. Запускаем User Service..."
        exec uvicorn app.main:app --host 0.0.0.0 --port 8001
        exit 0
    else
        echo "Таблица 'teams' не найдена, повтор через 2 секунды..."
        sleep 2
    fi
done

echo "Таблица 'teams' так и не появилась, завершаем..."
exit 1
