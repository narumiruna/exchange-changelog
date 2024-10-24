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

COPY src src
COPY main.py .
COPY pyproject.toml .
COPY uv.lock .
COPY README.md .
COPY config config
RUN pip install --no-cache-dir .

CMD ["python", "main.py"]