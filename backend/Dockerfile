# Backend Dockerfile
FROM python:3.11

ARG TARGETOS
ARG TARGETARCH
ARG TARGETVARIANT

# Install system dependencies
RUN apt-get update && rm -rf /var/lib/apt/lists/*
RUN wget -O golang-migrate.deb https://github.com/golang-migrate/migrate/releases/download/v4.17.0/migrate.${TARGETOS}-${TARGETARCH}${TARGETVARIANT}.deb \
    && dpkg -i golang-migrate.deb \
    && rm golang-migrate.deb

# Install Poetry
RUN pip install poetry

# 安装 NLTK 和其他必要的包
RUN pip install --no-cache-dir nltk

# 下载常用的 NLTK 数据包到默认的 NLTK 数据目录
RUN python -m nltk.downloader -d /usr/local/share/nltk_data punkt wordnet averaged_perceptron_tagger

# Set the working directory
WORKDIR /backend

# Copy only dependencies
COPY pyproject.toml poetry.lock* ./

# Install all dependencies
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi


RUN groupadd -g 1001 backend \
    && useradd -u 1001 -g backend -s /bin/bash -m backend \
    && chown -R backend:backend /backend \
    && chmod -R 777 /backend

# Copy the rest of application code
COPY . .

#HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --start-interval=1s --retries=3 CMD [ "curl", "-f", "http://localhost:8000/health" ]

ENTRYPOINT [ "uvicorn", "app.server:app", "--host", "0.0.0.0", "--log-config", "log_config.json" ]
