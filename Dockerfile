# Используем официальный Python образ
FROM python:3.11-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Устанавливаем системные зависимости
RUN apt-get update && apt-get install -y \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Копируем файлы зависимостей
COPY requirements.txt .

# Устанавливаем Python зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Клонируем репозиторий
RUN git clone https://github.com/DArkadich/skalping.git /tmp/skalping

# Копируем файлы бота
COPY --from=0 /tmp/skalping/ .

# Делаем скрипты исполняемыми
RUN chmod +x run_bot.sh deploy.sh

# Создаем пользователя для безопасности
RUN useradd --create-home --shell /bin/bash botuser && \
    chown -R botuser:botuser /app

# Переключаемся на пользователя бота
USER botuser

# Создаем директорию для логов
RUN mkdir -p /app/logs

# Устанавливаем переменные окружения по умолчанию
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app
ENV LOG_LEVEL=INFO

# Открываем порт для мониторинга (опционально)
EXPOSE 8080

# Команда по умолчанию
CMD ["python3", "main.py"]
