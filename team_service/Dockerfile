FROM python:3.10-slim

WORKDIR /app

# Установка PostgreSQL-клиента для проверки доступности БД
RUN apt-get update && apt-get install -y postgresql-client && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 8002

ENTRYPOINT ["/entrypoint.sh"]
