# File: Dockerfile
# Purpose: Backend Docker image
# Dependencies: pyproject.toml, poetry.lock

FROM python:3.11-slim AS builder

WORKDIR /app

RUN pip install --no-cache-dir poetry==1.8.0

COPY pyproject.toml poetry.lock* ./
RUN poetry config virtualenvs.create false \
    && poetry install --no-dev --no-interaction --no-ansi --no-root

COPY app ./app

FROM python:3.11-slim AS runtime

WORKDIR /app

# OCR + PDF system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    poppler-utils \
    tesseract-ocr \
    tesseract-ocr-fra \
    tesseract-ocr-eng \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
COPY app ./app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
