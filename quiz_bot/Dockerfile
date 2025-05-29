# Используем официальный Python образ
FROM python:3.10-slim

# Рабочая директория внутри контейнера
WORKDIR /app

# Копируем файл с зависимостями (если есть)
COPY requirements.txt .

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь код в контейнер
COPY . .

# Команда, которая будет запускаться при старте контейнера
CMD ["python", "main.py"]
