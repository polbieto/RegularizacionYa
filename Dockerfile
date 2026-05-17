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

# Verify critical files are present (fails build if missing)
RUN test -f /app/.chainlit/config.toml || (echo "ERROR: .chainlit/config.toml not found in image!" && exit 1)
RUN test -f /app/public/disclaimer.js || (echo "ERROR: public/disclaimer.js not found in image!" && exit 1)
RUN grep -q "custom_js" /app/.chainlit/config.toml || (echo "ERROR: custom_js not in config.toml!" && exit 1)

ENV CHAINLIT_APP_ROOT=/app

EXPOSE 8080
CMD ["sh", "-c", "yoyo apply --database \"$APP_DATABASE_URL\" --batch ./migrations && chainlit run chatregularizacion/app.py --host 0.0.0.0 --port ${PORT:-8000}"]
