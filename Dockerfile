# Используем официальный образ Python 3.12 для Python-приложения
FROM python:3.12-slim AS python-builder
WORKDIR /app
COPY app/requirements.txt .
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/* \
    && python -m venv /opt/venv \
    && /opt/venv/bin/pip install --no-cache-dir --upgrade pip \
    && /opt/venv/bin/pip install --no-cache-dir -r requirements.txt \
    && apt-get purge -y --auto-remove build-essential

# Используем официальный образ Golang для Go-приложения
FROM golang:1.24.5-alpine AS go-builder
WORKDIR /app
COPY proxy/go.mod proxy/go.sum ./
RUN go mod download
COPY proxy/ .
RUN go build -o sl_helper .

# Финальный образ для Python-приложения
FROM python:3.12-slim AS python-app
ENV PATH="/opt/venv/bin:$PATH"
WORKDIR /app
COPY --from=python-builder /opt/venv /opt/venv
COPY app/ .
EXPOSE 8506
CMD ["python", "main.py"]

# Финальный образ для Go-приложения
FROM alpine:latest AS go-proxy
WORKDIR /app
COPY --from=go-builder /app/sl_helper .
# Копируем также директорию src с исходниками, если они нужны во время выполнения
COPY --from=go-builder /app/src ./src
# Устанавливаем переменные окружения
ENV BACKEND_HOST=python-app:8506
ENV DOCKER_MODE=true
EXPOSE 3000
CMD ["./sl_helper"]