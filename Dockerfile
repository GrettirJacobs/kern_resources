FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install gunicorn

# Copy application code
COPY . .

# Create directory for SQLite database
RUN mkdir -p /app/data
ENV SQLITE_DB_PATH=/app/data/entries.db

# Expose port
EXPOSE 10000

# Start Gunicorn
CMD gunicorn --config gunicorn_config.py "kern_resources.app:app"