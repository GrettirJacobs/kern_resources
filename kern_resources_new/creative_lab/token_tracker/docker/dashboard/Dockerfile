FROM python:3.10-slim

WORKDIR /app

# Copy requirements file
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY . .

# Create logs directory
RUN mkdir -p logs

# Expose port
EXPOSE 8050

# Set environment variables
ENV PYTHONPATH=/app

# Run the dashboard
CMD ["python", "-m", "token_tracker.dashboard.app"]
