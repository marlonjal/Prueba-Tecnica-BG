# Use the official image so Chromium and its Linux dependencies stay compatible.
FROM mcr.microsoft.com/playwright/python:v1.52.0-noble

# Keep every application path stable inside local and CI containers.
WORKDIR /app

# Disable bytecode files, stream logs immediately, and default to headless Chromium.
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PLAYWRIGHT_BROWSERS_PATH=/ms-playwright \
    HEADLESS=true

# Install pinned Python dependencies before copying source to maximize layer reuse.
COPY requirements.txt .
RUN --mount=type=cache,target=/root/.cache/pip pip install -r requirements.txt

# Copy the suite and guarantee that every ignored evidence directory exists.
COPY . .
RUN mkdir -p \
    /app/results/reports \
    /app/results/screenshots \
    /app/results/videos \
    /app/results/traces

# Run the non-destructive regression unless the caller supplies another command.
CMD ["python", "-m", "pytest", "-m", "not destructive"]
