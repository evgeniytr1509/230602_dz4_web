# Базовый образ Docker
FROM python:3.9-slim

# Установка зависимостей
RUN pip install ...

# Копирование файлов проекта
COPY . /app
WORKDIR /app

# Команда запуска приложения
CMD ["python", "main.py"]