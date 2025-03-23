version: '3.8'

services:
  web:
    build: ./app
    container_name: fastapi_app
    ports:
      - "8000:8000"
    depends_on:
      - db
      - redis
    environment:
      - DATABASE_URL=postgresql+asyncpg://postgres:postgres@db:5432/app_db
      - REDIS_URL=redis://redis:6379

  db:
    image: postgres:13
    container_name: fastapi_db
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
      POSTGRES_DB: app_db
    volumes:
      - pgdata:/var/lib/postgresql/data

  redis:
    image: redis:6.2
    container_name: fastapi_redis
    ports:
      - "6379:6379"

volumes:
  pgdata:
