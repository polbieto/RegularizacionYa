FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install poetry

COPY pyproject.toml poetry.lock ./
RUN poetry config virtualenvs.create false
RUN poetry install --no-root --without dev

COPY . /app

EXPOSE 8080
CMD ["sh", "-c", "yoyo apply --database \"$DATABASE_URL\" --batch ./migrations && chainlit run chatregularizacion/app.py -w --host 0.0.0.0 --port ${PORT:-8000}"]
