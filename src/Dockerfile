FROM python:3.11-slim

# Устанавливаем переменные окружения
# Предотвращает Python от записи скомпилированных байт-кодов `.pyc`
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED=1

# Устанавливаем рабочую директорию
WORKDIR /usr/app/src

# Устанавливаем зависимости Python
RUN pip install --upgrade pip "poetry==1.8.3"
# Отключение создания виртуального окружения
RUN poetry config virtualenvs.create false --local
COPY pyproject.toml poetry.lock ./

RUN poetry install

# Копируем весь проект в контейнер
COPY . /usr/src/app

# Указываем, что контейнер будет слушать на порту 8000
EXPOSE 8000
