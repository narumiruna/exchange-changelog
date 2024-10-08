FROM python:3.11-slim

RUN apt-get update \
    && apt-get install -y \
    chromium \
    git \
    nodejs \
    npm \
    && rm -rf /var/lib/apt/lists/*

RUN npm install -g single-file-cli

WORKDIR /app

COPY changelog_helper changelog_helper
COPY main.py .
COPY pyproject.toml .
COPY poetry.lock .
COPY README.md .
RUN pip install --no-cache-dir .
