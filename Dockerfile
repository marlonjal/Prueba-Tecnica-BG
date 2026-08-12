FROM mcr.microsoft.com/playwright/python:v1.52.0-noble

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PLAYWRIGHT_BROWSERS_PATH=/ms-playwright \
    HEADLESS=true

COPY requirements.txt .
RUN --mount=type=cache,target=/root/.cache/pip pip install -r requirements.txt

COPY . .
RUN mkdir -p \
    /app/results/reports \
    /app/results/screenshots \
    /app/results/videos \
    /app/results/traces

CMD ["python", "-m", "pytest", "-m", "not destructive"]
