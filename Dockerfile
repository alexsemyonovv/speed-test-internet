FROM python:3.12-slim

WORKDIR /app

RUN pip install poetry==2.1.3 && \
    poetry config virtualenvs.create false

COPY pyproject.toml poetry.lock ./
RUN poetry install --only main --no-root

COPY . .

ENTRYPOINT ["python", "main.py"]
