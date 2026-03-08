FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy project files
COPY pyproject.toml ./
COPY src ./src
COPY alembic ./alembic
COPY alembic.ini ./

# Install Python dependencies
RUN pip install --no-cache-dir -e .

# Run migrations and start bot
CMD ["sh", "-c", "alembic upgrade head && python -m src.main"]
